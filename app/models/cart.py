# Third-party imports
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Local application imports
from app.core.database import Base


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    size = Column(String(10), nullable=False)  # Selected size
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product")  # Removed back_populates to avoid circular import

    def __repr__(self):
        return f"<CartItem(user_id='{self.user_id}', product_id='{self.product_id}', size='{self.size}', quantity={self.quantity})>"
