import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

# =========================================================================
# ENHANCED ENVIRONMENT & SECURITY CONFIGURATION
# =========================================================================
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_THIS_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# =========================================================================
# CRYPTOGRAPHIC PASSWORD HASHING OPERATIONS
# =========================================================================
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# =========================================================================
# STATE-PRESERVED TOKENS ARCHITECTURE
# =========================================================================
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        # Handles raw token header string mapping if extracted out of standard cookies
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def get_current_user(user_data: dict = Depends(verify_token)) -> dict:
    return user_data

# =========================================================================
# COMPATIBLE SECURITY ASSIGNMENT STRATEGIES
# =========================================================================
def verify_admin(user_data: dict = Depends(verify_token)) -> dict:
    if user_data.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user_data

def verify_lawyer(user_data: dict = Depends(verify_token)) -> dict:
    if user_data.get("role") != "lawyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Lawyer access required"
        )
    return user_data

def verify_client(user_data: dict = Depends(verify_token)) -> dict:
    if user_data.get("role") != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client access required"
        )
    return user_data

def verify_roles(allowed_roles: list):
    def role_checker(user_data: dict = Depends(verify_token)) -> dict:
        if user_data.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        return user_data
    return role_checker