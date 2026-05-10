import os

JWT_SECRET                = os.getenv("JWT_SECRET", "dev-secret")
ALGORITHM                 = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 8
