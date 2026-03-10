import os
import uuid
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from app.services.pdf_service import PDFService
from app.services.rag_service import RAGService
from app.core.session_manager import session_manager
from langchain_community.vectorstores import FAISS

app = FastAPI(title="DocuChat AI API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
# In production, these would be injected or loaded from env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-key-here")
pdf_service = PDFService()
rag_service = RAGService(api_key=OPENAI_API_KEY)

@app.post("/v1/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Uploads PDFs, extracts text, and builds/updates the FAISS index for the session."""
    session_id = str(uuid.uuid4())  # Simplified: In a real app, this comes from a header/cookie
    
    all_docs = []
    for file in files:
        if not file.filename.endswith(".pdf"):
            continue
        content = await file.read()
        docs = pdf_service.process_pdf(content, file.filename)
        all_docs.extend(docs)
    
    if not all_docs:
        raise HTTPException(status_code=400, detail="No valid PDF content found.")

    # Create or update FAISS index
    vector_store = FAISS.from_documents(all_docs, rag_service.embeddings)
    session_manager.set_vector_store(session_id, vector_store)
    
    return {
        "session_id": session_id,
        "message": f"Successfully processed {len(files)} files.",
        "chunk_count": len(all_docs)
    }

@app.post("/v1/chat")
async def chat(
    session_id: str = Body(..., embed=True),
    message: str = Body(..., embed=True)
):
    """Queries the RAG pipeline for a specific session."""
    vector_store = session_manager.get_vector_store(session_id)
    if not vector_store:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    
    response = await rag_service.get_answer(vector_store, message)
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
