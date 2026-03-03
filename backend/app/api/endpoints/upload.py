from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.pdf_service import PDFService
from app.services.vector_service import VectorService
import uuid

router = APIRouter()
vector_service = VectorService()

@app.post("/upload") # Note: router.post is used in actual file, but app.post for clarity here
async def upload_document(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    content = await file.read()
    documents = await PDFService.process_pdf(content, file.filename)
    await vector_service.add_documents(documents, session_id)
    
    return {"file_id": str(uuid.uuid4()), "filename": file.filename, "status": "processed"}
