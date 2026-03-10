from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from typing import List
import uuid
from app.services.pdf_service import PDFService
from app.services.rag_service import rag_service
from app.core.session_manager import session_manager
from pydantic import BaseModel

router = APIRouter()
pdf_service = PDFService()

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]

@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    session_id = str(uuid.uuid4())
    all_docs = []
    
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per session.")

    for file in files:
        if not file.filename.endswith(".pdf"):
            continue
        content = await file.read()
        docs = pdf_service.extract_documents(content, file.filename)
        all_docs.extend(docs)
    
    if not all_docs:
        raise HTTPException(status_code=400, detail="No valid text found in uploaded PDFs.")

    vector_store = rag_service.create_vector_store(all_docs)
    session_manager.set_index(session_id, vector_store)
    
    return {"session_id": session_id, "status": "processed", "file_count": len(files)}

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    vector_store = session_manager.get_index(request.session_id)
    if not vector_store:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    
    result = await rag_service.get_answer(vector_store, request.message)
    return result
