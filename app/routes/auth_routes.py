from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    OAuth2PasswordRequestForm
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.user_model import (
    User
)

from app.schemas.user_schema import (
    UserCreate
)

from app.services.auth_service import (

    hash_password,

    verify_password,

    create_access_token,

    verify_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)



# =========================
# REGISTER USER
# =========================

@router.post("/register")
def register_user(

    user: UserCreate,

    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(

        User.email == user.email

    ).first()



    if existing_user:

        raise HTTPException(

            status_code=400,

            detail="Email already registered"
        )



    # HASH PASSWORD
    hashed_password = hash_password(
        user.password
    )



    # CREATE USER
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

        "message":
        "User registered successfully",

        "user": {

            "id":
            new_user.id,

            "full_name":
            new_user.full_name,

            "email":
            new_user.email,

            "role":
            new_user.role
        }
    }



# =========================
# LOGIN USER
# =========================

@router.post("/login")
def login(

    form_data: OAuth2PasswordRequestForm = Depends(),

    db: Session = Depends(get_db)
):

    db_user = db.query(User).filter(

        User.email == form_data.username

    ).first()



    # USER NOT FOUND
    if not db_user:

        raise HTTPException(

            status_code=404,

            detail="User not found"
        )



    # INVALID PASSWORD
    if not verify_password(

        form_data.password,

        db_user.password
    ):

        raise HTTPException(

            status_code=401,

            detail="Invalid password"
        )



    # CREATE JWT TOKEN
    access_token = create_access_token(

        data={

            "user_id":
            db_user.id,

            "email":
            db_user.email,

            "role":
            db_user.role
        }
    )



    return {

        "message":
        "Login successful",

        "access_token":
        access_token,

        "token_type":
        "bearer",

        "user": {

            "id":
            db_user.id,

            "full_name":
            db_user.full_name,

            "email":
            db_user.email,

            "role":
            db_user.role
        }
    }



# =========================
# GET CURRENT USER
# =========================

@router.get("/me")
def get_current_user(

    user_data: dict = Depends(
        verify_token
    ),

    db: Session = Depends(get_db)
):

    user = db.query(User).filter(

        User.id == user_data["user_id"]

    ).first()



    if not user:

        raise HTTPException(

            status_code=404,

            detail="User not found"
        )



    return {

        "id":
        user.id,

        "full_name":
        user.full_name,

        "email":
        user.email,

        "role":
        user.role,

        "phone_number":
        user.phone_number
    }



# =========================
# VERIFY TOKEN
# =========================

@router.get("/verify")
def verify_user_token(

    user_data: dict = Depends(
        verify_token
    )
):

    return {

        "valid":
        True,

        "user":
        user_data
    }



# =========================
# ADMIN CHECK
# =========================

@router.get("/admin-check")
def admin_check(

    user_data: dict = Depends(
        verify_token
    )
):

    if user_data["role"] != "admin":

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail="Admin access required"
        )



    return {

        "message":
        "Admin access granted"
    }