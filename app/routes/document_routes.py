import os
import shutil
import uuid

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException
)

from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models.document_model import (
    Document
)

from app.models.case_model import (
    Case
)

from app.services.auth_service import (
    verify_token
)

from app.services.timeline_service import (
    create_timeline_event
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)



# =========================
# UPLOAD DIRECTORY
# =========================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "..",
    "uploads"
)

UPLOAD_FOLDER = os.path.abspath(
    UPLOAD_FOLDER
)


os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)



# =========================
# DATABASE CONNECTION
# =========================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()



# =========================
# UPLOAD DOCUMENT
# =========================

@router.post("/{case_id}")
def upload_document(

    case_id: int,

    file: UploadFile = File(...),

    db: Session = Depends(get_db),

    user_data: dict = Depends(verify_token)
):

    case = db.query(Case).filter(
        Case.id == case_id
    ).first()


    if not case:

        raise HTTPException(

            status_code=404,

            detail="Case not found"
        )



    # =========================
    # FILE VALIDATION
    # =========================

    allowed_extensions = [
        ".pdf",
        ".docx"
    ]


    file_extension = os.path.splitext(
        file.filename
    )[1].lower()


    if file_extension not in allowed_extensions:

        raise HTTPException(

            status_code=400,

            detail="Only PDF and DOCX files allowed"
        )



    # =========================
    # UNIQUE FILENAME
    # =========================

    unique_filename = (

        f"{uuid.uuid4()}"
        f"{file_extension}"
    )


    file_path = os.path.join(
        UPLOAD_FOLDER,
        unique_filename
    )



    # =========================
    # SAVE FILE
    # =========================

    try:

        with open(file_path, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

    except Exception:

        raise HTTPException(

            status_code=500,

            detail="Failed to upload file"
        )



    # =========================
    # SAVE DATABASE
    # =========================

    document = Document(

        case_id=case_id,

        filename=unique_filename,

        filepath=file_path
    )

    db.add(document)

    db.commit()

    db.refresh(document)



    # =========================
    # TIMELINE EVENT
    # =========================

    create_timeline_event(

        db=db,

        case_id=case_id,

        title="Document Uploaded",

        description=f"""

Filename:
{unique_filename}

Document uploaded successfully.

        """
    )



    return {

        "message":
        "Document uploaded successfully",

        "document_id":
        document.id,

        "filename":
        unique_filename
    }



# =========================
# GET DOCUMENTS
# =========================

@router.get("/{case_id}")
def get_documents(

    case_id: int,

    db: Session = Depends(get_db),

    user_data: dict = Depends(verify_token)
):

    case = db.query(Case).filter(
        Case.id == case_id
    ).first()


    if not case:

        raise HTTPException(

            status_code=404,

            detail="Case not found"
        )


    documents = db.query(Document).filter(

        Document.case_id == case_id

    ).order_by(

        Document.id.desc()

    ).all()


    results = []


    for document in documents:

        results.append({

            "id":
            document.id,

            "case_id":
            document.case_id,

            "filename":
            document.filename,

            "filepath":
            document.filepath
        })


    return results



# =========================
# DOWNLOAD DOCUMENT
# =========================

@router.get("/download/{document_id}")
def download_document(

    document_id: int,

    db: Session = Depends(get_db),

    user_data: dict = Depends(verify_token)
):

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()


    if not document:

        raise HTTPException(

            status_code=404,

            detail="Document not found"
        )



    # FILE EXISTS CHECK
    if not os.path.exists(
        document.filepath
    ):

        raise HTTPException(

            status_code=404,

            detail="File missing from server"
        )



    return FileResponse(

        path=document.filepath,

        filename=document.filename,

        media_type="application/octet-stream"
    )



# =========================
# DELETE DOCUMENT
# =========================

@router.delete("/{document_id}")
def delete_document(

    document_id: int,

    db: Session = Depends(get_db),

    user_data: dict = Depends(verify_token)
):

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()


    if not document:

        raise HTTPException(

            status_code=404,

            detail="Document not found"
        )



    document_case_id = document.case_id

    document_filename = document.filename



    # DELETE FILE
    if os.path.exists(
        document.filepath
    ):

        try:

            os.remove(
                document.filepath
            )

        except Exception:

            pass



    # DELETE DATABASE RECORD
    db.delete(document)

    db.commit()



    # =========================
    # TIMELINE EVENT
    # =========================

    create_timeline_event(

        db=db,

        case_id=document_case_id,

        title="Document Deleted",

        description=f"""

Filename:
{document_filename}

Document deleted successfully.

        """
    )



    return {

        "message":
        "Document deleted successfully"
    }