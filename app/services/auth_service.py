from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer


SECRET_KEY = "MYSECRETKEY123"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# Hash Password
def hash_password(password: str):
    return pwd_context.hash(password)


# Verify Password
def verify_password(
    plain_password,
    hashed_password
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# Create JWT Token
def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


# Verify JWT Token
def verify_token(
    token: str = Depends(oauth2_scheme)
):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
# Admin Role Verification
def verify_admin(
    user_data: dict = Depends(verify_token)
):

    if user_data.get("role") != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return user_data
# Lawyer Role Verification
def verify_lawyer(
    user_data: dict = Depends(verify_token)
):

    if user_data.get("role") != "lawyer":

        raise HTTPException(
            status_code=403,
            detail="Lawyer access required"
        )

    return user_data


# Client Role Verification
def verify_client(
    user_data: dict = Depends(verify_token)
):

    if user_data.get("role") != "client":

        raise HTTPException(
            status_code=403,
            detail="Client access required"
        )

    return user_data


# Get Current Logged User
def get_current_user(
    user_data: dict = Depends(verify_token)
):

    return user_data    
    