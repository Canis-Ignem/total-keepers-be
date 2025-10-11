### Guide to Implementing Secure Checkout with RedSYS Payments, Discount Codes, and Best Practices

This guide provides a step-by-step process for integrating RedSYS (a popular Spanish payment gateway) into your Next.js front-end, FastAPI back-end, and PostgreSQL database setup. The focus is on the redirect-based payment flow (the most common and secure method for RedSYS), which offloads sensitive card handling to RedSYS's hosted page, minimizing your PCI DSS compliance burden. We'll cover handling discount codes securely, ensuring no vulnerabilities like injection or tampering, and following industry best practices for security and reliability.

RedSYS uses HMAC SHA256 signing for requests and responses to prevent tampering. We'll use the `python-redsys` library for the back-end (simple and lightweight) and handle the front-end via form submission. Always test in RedSYS's sandbox environment before going live.

#### Prerequisites
1. **RedSYS Credentials**: Obtain from your bank or RedSYS dashboard:
   - Merchant Code (e.g., FUC or Merchant ID).
   - Terminal Number (usually "1" for standard).
   - Secret Key (for HMAC SHA256 signing—keep this secret!).
   - Sandbox URLs: Use `https://sis-t.redsys.es/sis/operaciones` for testing; switch to `https://sis.redsys.es/sis/operaciones` for production.
   - Notification URL: Your back-end endpoint for callbacks (e.g., `/redsys/callback`).

2. **Environment Setup**:
   - Store credentials securely in environment variables (e.g., via `.env` files or secrets managers like AWS Secrets Manager). Never hardcode them.
   - Ensure your entire app uses HTTPS (e.g., via Let's Encrypt or Vercel for Next.js).
   - Install dependencies:
     - Back-end: `pip install python-redsys uvicorn` (for FastAPI).
     - Front-end: No specific RedSYS library needed; use native forms.

3. **Database Schema (PostgreSQL)**:
   - Create tables for orders and discount codes:
     ```sql
     CREATE TABLE orders (
         id SERIAL PRIMARY KEY,
         order_id VARCHAR(12) UNIQUE NOT NULL,  -- Unique RedSYS-compatible order ID (e.g., alphanumeric, 4-12 chars)
         user_id INTEGER NOT NULL,  -- Reference to your users table
         total_amount DECIMAL(10, 2) NOT NULL,
         discounted_amount DECIMAL(10, 2) NOT NULL,
         status VARCHAR(20) DEFAULT 'pending' NOT NULL,  -- pending, paid, failed, canceled
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
     );

     CREATE TABLE discount_codes (
         id SERIAL PRIMARY KEY,
         code VARCHAR(20) UNIQUE NOT NULL,
         discount_percentage DECIMAL(5, 2) NOT NULL,  -- e.g., 10.00 for 10%
         max_uses INTEGER,  -- Optional: Limit total uses
         uses INTEGER DEFAULT 0,
         expires_at TIMESTAMP,  -- Optional: Expiration date
         active BOOLEAN DEFAULT TRUE
     );
     ```
   - Use an ORM like SQLAlchemy for FastAPI integration.

4. **Security Fundamentals**:
   - **No Card Data on Your Servers**: RedSYS handles this via redirect—your app never sees card details.
   - **Input Validation**: Sanitize all user inputs (e.g., discount codes, amounts) to prevent SQL injection or XSS. Use libraries like `pydantic` in FastAPI.
   - **Idempotency**: Use unique order IDs to handle retries or duplicates.
   - **Rate Limiting**: Apply to checkout endpoints to prevent abuse (e.g., via FastAPI middleware).
   - **Logging**: Log errors and transactions without sensitive data (e.g., no full parameters).
   - **Compliance**: Follow PCI DSS Level 4 (for low-volume merchants) by using redirect. Audit for GDPR (Spain/EU) on user data.
   - **Error Handling**: Gracefully handle failures (e.g., invalid signatures) and notify admins.
   - **Testing**: Use RedSYS sandbox. Simulate discounts and failures.

#### Step 1: Implement Discount Code Handling (Back-End)
Discounts should be validated and applied on the back-end to prevent client-side tampering.

- In FastAPI, create an endpoint to validate and apply codes:
  ```python
  from decimal import Decimal
  from fastapi import FastAPI, HTTPException, Depends
  from pydantic import BaseModel
  from sqlalchemy import create_engine, Column, Integer, String, Decimal as SQLDecimal, Boolean, DateTime
  from sqlalchemy.ext.declarative import declarative_base
  from sqlalchemy.orm import sessionmaker, Session

  app = FastAPI()
  engine = create_engine("postgresql://user:pass@localhost/dbname")
  SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
  Base = declarative_base()

  # Models (extend as needed)
  class DiscountCode(Base):
      __tablename__ = "discount_codes"
      id = Column(Integer, primary_key=True)
      code = Column(String, unique=True)
      discount_percentage = Column(SQLDecimal(5, 2))
      # ... other fields

  class ApplyDiscountRequest(BaseModel):
      code: str
      original_amount: Decimal

  def get_db():
      db = SessionLocal()
      try:
          yield db
      finally:
          db.close()

  @app.post("/apply-discount")
  def apply_discount(request: ApplyDiscountRequest, db: Session = Depends(get_db)):
      discount = db.query(DiscountCode).filter(DiscountCode.code == request.code, DiscountCode.active == True).first()
      if not discount or (discount.expires_at and discount.expires_at < datetime.now()):
          raise HTTPException(status_code=400, detail="Invalid or expired discount code")
      if discount.max_uses and discount.uses >= discount.max_uses:
          raise HTTPException(status_code=400, detail="Discount code usage limit reached")

      discounted_amount = request.original_amount * (Decimal(1) - (discount.discount_percentage / Decimal(100)))
      if discounted_amount < 0:
          raise HTTPException(status_code=400, detail="Invalid amount after discount")

      # Optionally increment uses
      discount.uses += 1
      db.commit()

      return {"discounted_amount": discounted_amount.quantize(Decimal("0.01"))}
  ```
- Best Practices: 
  - Validate code existence, expiration, and limits in DB.
  - Use `Decimal` for precise money calculations (avoid floats).
  - Ensure amounts can't go negative.

#### Step 2: Create Order and Initiate Payment (Back-End)
- Endpoint to create order, apply final amount (post-discount), and generate RedSYS form params.
  ```python
  from redsys.client import RedirectClient
  from redsys.constants import EUR, STANDARD_PAYMENT
  import os
  from decimal import Decimal, ROUND_HALF_UP
  from pydantic import BaseModel

  REDSYS_SECRET_KEY = os.getenv("REDSYS_SECRET_KEY")
  REDSYS_MERCHANT_CODE = os.getenv("REDSYS_MERCHANT_CODE")
  REDSYS_TERMINAL = os.getenv("REDSYS_TERMINAL")
  client = RedirectClient(REDSYS_SECRET_KEY)

  class CheckoutRequest(BaseModel):
      user_id: int
      amount: Decimal  # Post-discount amount
      discount_code: str | None = None  # Optional

  @app.post("/checkout")
  def checkout(request: CheckoutRequest, db: Session = Depends(get_db)):
      # If discount_code, validate and apply (or assume pre-applied)
      final_amount = request.amount.quantize(Decimal("0.01"), ROUND_HALF_UP)

      # Generate unique order_id (e.g., sequential or UUID prefix)
      order_id = f"ORD{db.query(func.count(orders.id)).scalar() + 1:08d}"

      # Save order as pending
      new_order = orders(order_id=order_id, user_id=request.user_id, discounted_amount=final_amount, status="pending")
      db.add(new_order)
      db.commit()

      # Prepare RedSYS parameters
      parameters = {
          "merchant_code": REDSYS_MERCHANT_CODE,
          "terminal": REDSYS_TERMINAL,
          "transaction_type": STANDARD_PAYMENT,
          "currency": EUR,
          "order": order_id,
          "amount": final_amount,
          "merchant_data": f"User {request.user_id} order",
          "merchant_name": "Your Store Name",
          "titular": "Your Company Ltd.",
          "product_description": "Products purchase",
          "merchant_url": "https://your-backend.com/redsys/callback",  # Callback URL
      }

      try:
          form_params = client.prepare_request(parameters)
      except Exception as e:
          raise HTTPException(status_code=500, detail=f"Payment initiation failed: {str(e)}")

      # Return form params for front-end to submit
      return form_params
  ```
- Best Practices:
  - Generate order_id server-side to prevent tampering.
  - Sign parameters with HMAC SHA256 (handled by library).
  - Use sandbox/production toggle via env var.

#### Step 3: Front-End Checkout (Next.js)
- Create a checkout page that calls the back-end, then auto-submits the form to RedSYS.
  ```jsx
  // pages/checkout.tsx
  import { useState } from 'react';

  export default function Checkout() {
    const [formParams, setFormParams] = useState(null);

    const handleCheckout = async (e) => {
      e.preventDefault();
      const formData = new FormData(e.target);
      const response = await fetch('/api/checkout-proxy', {  // Proxy to FastAPI if needed
        method: 'POST',
        body: JSON.stringify({
          user_id: 1,  // From auth
          amount: formData.get('amount'),
          discount_code: formData.get('discount_code'),
        }),
        headers: { 'Content-Type': 'application/json' },
      });
      const params = await response.json();
      setFormParams(params);

      // Auto-submit
      if (params) document.getElementById('redsys-form').submit();
    };

    return (
      <form onSubmit={handleCheckout}>
        <input name="amount" type="number" placeholder="Amount" required />
        <input name="discount_code" type="text" placeholder="Discount Code" />
        <button type="submit">Checkout</button>
      </form>
      {formParams && (
        <form id="redsys-form" action="https://sis-t.redsys.es/sis/operaciones" method="POST" style={{ display: 'none' }}>
          <input type="hidden" name="Ds_SignatureVersion" value={formParams.Ds_SignatureVersion} />
          <input type="hidden" name="Ds_MerchantParameters" value={formParams.Ds_MerchantParameters} />
          <input type="hidden" name="Ds_Signature" value={formParams.Ds_Signature} />
        </form>
      )}
    );
  }
  ```
- Best Practices:
  - Use CSR for form submission to avoid exposing keys.
  - If cross-origin (Next.js to FastAPI), use CORS middleware in FastAPI.
  - Validate form inputs client-side for UX, but rely on back-end for security.

#### Step 4: Handle Payment Callback (Back-End)
- RedSYS POSTs to your `merchant_url` on completion.
  ```python
  from fastapi import Request, HTTPException

  @app.post("/redsys/callback")
  async def redsys_callback(request: Request, db: Session = Depends(get_db)):
      params = await request.form()
      signature = params.get("Ds_Signature")
      merchant_params = params.get("Ds_MerchantParameters")

      try:
          response = client.create_response(signature, merchant_params)
      except ValueError:
          # Invalid signature - possible tampering
          raise HTTPException(status_code=400, detail="Invalid payment response")

      order = db.query(orders).filter(orders.order_id == response.order).first()
      if not order:
          raise HTTPException(status_code=404, detail="Order not found")

      if response.is_paid:
          order.status = "paid"
      elif response.is_canceled:
          order.status = "canceled"
      else:
          order.status = "failed"

      db.commit()

      # Redirect user (RedSYS expects HTML response for redirect)
      if order.status == "paid":
          return HTMLResponse(content="<script>window.location = 'https://your-frontend.com/success';</script>")
      else:
          return HTMLResponse(content="<script>window.location = 'https://your-frontend.com/failure';</script>")
  ```
- Best Practices:
  - Validate signature to ensure response is from RedSYS.
  - Update DB transactionally (use locks if high concurrency).
  - Handle duplicates: Check if order already processed.
  - RedSYS may send notifications via POST; ensure endpoint is public but rate-limited.

#### Step 5: Front-End Success/Failure Pages
- Simple Next.js pages (`/success`, `/failure`) to show results and perhaps poll back-end for order status.

#### Step 6: Additional Best Practices and Vulnerabilities to Avoid
- **Discount-Specific**: Validate codes server-side only. Track usage to prevent reuse. Log applications for auditing.
- **Common Vulnerabilities**:
  - **CSRF/XSS**: Use CSRF tokens in forms; sanitize outputs.
  - **SQL Injection**: Use parameterized queries or ORM.
  - **Man-in-the-Middle**: Enforce HTTPS; use HSTS.
  - **Replay Attacks**: Unique order IDs and timestamps.
  - **Overpayments/Underpayments**: Recalculate amounts on callback.
- **Monitoring**: Integrate logging (e.g., Sentry) and alerts for failed payments.
- **Testing**: 
  - Unit test endpoints.
  - End-to-end: Simulate payments in sandbox (RedSYS provides test cards).
  - Load test for concurrency.
- **Deployment**: Use Vercel for Next.js, Render/GCP for FastAPI. Scale DB with read replicas if needed.
- **Edge Cases**: Handle network failures, partial payments, refunds (via RedSYS dashboard or API if supported).

This setup ensures secure, vulnerability-free payments. If you need refunds or subscriptions, check RedSYS docs for advanced features. Consult RedSYS support for Spain-specific compliance.