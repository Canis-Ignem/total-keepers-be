import calendar
import os

from dotenv import load_dotenv
from jose import jwt

load_dotenv()

# Secret and algorithm
SECRET_KEY = os.getenv("JWT_SECRET", "jwt_secret_key")
print(SECRET_KEY)
ALGORITHM = "HS256"

# Example payload for AnonymousUser JWT authentication
# Set expiration to December 31, 2025, 23:59:59 UTC
exp_timestamp = calendar.timegm((2025, 12, 31, 23, 59, 59, 0, 0, 0))
payload = {
    "sub": "1",
    "username": "front-end",
    "roles": ["service"],
    "exp": exp_timestamp,
}

token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
print("Generated JWT token:")
print(token)
