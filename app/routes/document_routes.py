import os
import shutil
import uuid
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException,
    status
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

# Import unified resources from your central app modules
from app.database import get_db  
from app.models.document_model import Document
from app.models.case_model import Case
from app.routes.auth_routes import get_current_user_payload  # FIXES 401 UNAUTHORIZED
from app.services.timeline_service import create_timeline_event

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

# =========================
# UPLOAD DIRECTORY
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.abspath(os.path.join(BASE_DIR, "..", "uploads"))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ==================================================
# GET ALL DOCUMENTS (FIXES 404/401 FOR /list PATH)
# ==================================================
@router.get("/list")
def list_all_documents(
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user_payload)
):
    """
    Handles global document collection requests. Admins can view everything,
    while standard users receive a clean overview.
    """
    documents = db.query(Document).order_by(Document.id.desc()).all()
    
    return [{
        "id": doc.id,
        "case_id": doc.case_id,
        "filename": doc.filename,
        "filepath": doc.filepath
    } for doc in documents]


# =========================
# UPLOAD DOCUMENT
# =========================
@router.post("/{case_id}")
def upload_document(
    case_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user_payload)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found"
        )

    # File format verification validation guards
    allowed_extensions = [".pdf", ".docx"]
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files allowed"
        )

    # Generate isolated unique filenames to prevent disk overwrite collisions
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to upload file"
        )

    # Save database track index
    document = Document(
        case_id=case_id,
        filename=unique_filename,
        filepath=file_path
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # Register system historic milestone logs
    create_timeline_event(
        db=db,
        case_id=case_id,
        title="Document Uploaded",
        description=f"Filename:\n{unique_filename}\n\nDocument uploaded successfully."
    )

    return {
        "message": "Document uploaded successfully",
        "document_id": document.id,
        "filename": unique_filename
    }


# =========================
# GET DOCUMENTS BY CASE
# =========================
@router.get("/{case_id}")
def get_documents(
    case_id: int,
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user_payload)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found"
        )

    documents = db.query(Document).filter(
        Document.case_id == case_id
    ).order_by(Document.id.desc()).all()

    return [{
        "id": doc.id,
        "case_id": doc.case_id,
        "filename": doc.filename,
        "filepath": doc.filepath
    } for doc in documents]


# =========================
# DOWNLOAD DOCUMENT
# =========================
@router.get("/download/{document_id}")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user_payload)
):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    if not os.path.exists(document.filepath):
        raise HTTPException(
            status_code=404,
            detail="File missing from server filesystem tracking storage"
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
    user_data: dict = Depends(get_current_user_payload)
):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    document_case_id = document.case_id
    document_filename = document.filename

    # Unlink physical asset volume storage trace safely
    if os.path.exists(document.filepath):
        try:
            os.remove(document.filepath)
        except Exception:
            pass

    db.delete(document)
    db.commit()

    # Append systemic metric telemetry logging
    create_timeline_event(
        db=db,
        case_id=document_case_id,
        title="Document Deleted",
        description=f"Filename:\n{document_filename}\n\nDocument deleted successfully."
    )

    return {
        "message": "Document deleted successfully"
    }