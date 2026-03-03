from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import uuid
from app.services.pdf_service import PDFService
from app.services.vector_store import VectorStoreService
from app.services.llm_service import LLMService
from app.models.schemas import ChatRequest, ChatResponse
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
pdf_service = PDFService()
vector_store = VectorStoreService(api_key=os.getenv("GOOGLE_API_KEY"))
llm_service = LLMService(api_key=os.getenv("GOOGLE_API_KEY"))

@router.post("/upload")
async def upload_documents(
    session_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    processed_files = []
    for file in files:
        if not file.filename.endswith(".pdf"):
            continue
        
        content = await file.read()
        chunks = pdf_service.process_pdf(content, file.filename)
        vector_store.add_documents(session_id, chunks)
        processed_files.append(file.filename)
    
    return {"status": "success", "files": processed_files}

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # 1. Retrieve relevant chunks
    context_docs = vector_store.similarity_search(request.session_id, request.query)
    
    if not context_docs:
        return ChatResponse(
            answer="I don't have any documents to reference. Please upload some PDFs first.",
            sources=[]
        )

    # 2. Generate answer using LLM
    answer, sources = await llm_service.generate_answer(request.query, context_docs, request.history)
    
    return ChatResponse(answer=answer, sources=sources)
