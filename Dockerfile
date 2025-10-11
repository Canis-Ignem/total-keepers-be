# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app"


ENV REDSYS_SANDBOX=True
ENV REDSYS_MERCHANT_URL=https://total-keeper-db.whitemeadow-ce92d559.northeurope.azurecontainerapps.io/api/v1/payments/redsys-callback

# API Settings
ENV DEBUG=true
ENV ENVIRONMENT=development

# JWT Authentication settings
#JWT_SECRET=dc6f66b5a75b258d89080791c07058a53afb53a0ee31728315263641e6de1393
ENV JWT_ALGORITHM=HS256
ENV ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENV REFRESH_TOKEN_EXPIRE_DAYS=30



# GOOGLE
ENV GOOGLE_CREDENTIALS_FILE=keys/total-keepers-6492ff87b584.json
ENV NOREPLY_EMAIL=no-reply@totalkeepers.com
ENV ADMIN_EMAIL=admin@totalkeepers.com

# Gmail SMTP
ENV SMTP_SERVER=smtp.gmail.com
ENV SMTP_HOST=smtp.gmail.com
ENV SMTP_PORT=587
ENV SMTP_TLS=True
ENV SMTP_USERNAME=jonperezetxebarria@gmail.com
ENV SMTP_USER=jonperezetxebarria@gmail.com
ENV SMTP_FROM_EMAIL=jonperezetxebarria@gmail.com
ENV SMTP_FROM_NAME="Total Keepers"
ENV EMAIL_FROM=no-reply@totalkeepers.com
ENV FINANCE_EMAIL=totalkeepersbilbao@gmail.com


# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' --uid 1001 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]