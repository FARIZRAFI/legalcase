from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserCreate
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# ---------------- REGISTER USER ---------------- #

@router.post("/register")
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    # Check Existing User
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash Password
    hashed_password = hash_password(user.password)

    # Create User
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password=hashed_password,
        role=user.role,
        phone_number=user.phone_number
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id
    }


# ---------------- LOGIN USER ---------------- #

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Find User
    db_user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    # User Not Found
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Verify Password
    if not verify_password(
        form_data.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    # Create JWT Token
    access_token = create_access_token(
        data={
            "user_id": db_user.id,
            "email": db_user.email,
            "role": db_user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }