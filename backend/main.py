from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from .core.rag_engine import rag_manager

app = FastAPI(title="DocuChat AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    message: str
    history: Optional[List[dict]] = []

@app.post("/upload")
async def upload_file(session_id: str = Form(...), file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    content = await file.read()
    success = await rag_manager.process_pdf(content, file.filename, session_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to process PDF.")
    
    return {"status": "success", "file_name": file.filename}

@app.post("/chat")
async def chat(request: ChatRequest):
    response = await rag_manager.chat(request.session_id, request.message, request.history)
    return response

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
