import os

from sqlalchemy import (
    create_engine
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker
)



# =========================
# DATABASE URL
# =========================

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)



# =========================
# VALIDATION
# =========================

if not DATABASE_URL:

    raise Exception(
        "DATABASE_URL environment variable not set"
    )



# =========================
# RAILWAY POSTGRES FIX
# =========================

# Railway sometimes provides:
# postgres://
# instead of:
# postgresql://

if DATABASE_URL.startswith(
    "postgres://"
):

    DATABASE_URL = DATABASE_URL.replace(

        "postgres://",

        "postgresql://",

        1
    )



# =========================
# SSL MODE FIX
# =========================

if "sslmode" not in DATABASE_URL:

    if "?" in DATABASE_URL:

        DATABASE_URL += "&sslmode=require"

    else:

        DATABASE_URL += "?sslmode=require"



# =========================
# CREATE ENGINE
# =========================

engine = create_engine(

    DATABASE_URL,

    pool_pre_ping=True,

    pool_size=5,

    max_overflow=10,

    echo=False
)



# =========================
# SESSION
# =========================

SessionLocal = sessionmaker(

    autocommit=False,

    autoflush=False,

    bind=engine
)



# =========================
# BASE CLASS
# =========================

Base = declarative_base()



# =========================
# DATABASE DEPENDENCY
# =========================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()