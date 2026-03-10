from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
import uuid
from app.services.pdf_service import PDFService
from app.services.rag_service import RAGService
from app.core.session_manager import session_manager
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)
pdf_service = PDFService()
rag_service = RAGService(api_key=settings.OPENAI_API_KEY)

@app.post("/v1/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    if len(files) > settings.MAX_FILES_PER_SESSION:
        raise HTTPException(status_code=400, detail=f"Maximum {settings.MAX_FILES_PER_SESSION} files allowed.")
    
    session_id = str(uuid.uuid4())
    all_docs = []
    
    for file in files:
        if not file.filename.endswith(".pdf"):
            continue
        content = await file.read()
        docs = pdf_service.process_pdf(content, file.filename)
        all_docs.extend(docs)
    
    if not all_docs:
        raise HTTPException(status_code=400, detail="No valid PDF text found.")
    
    vector_store = rag_service.create_vector_store(all_docs)
    session_manager.set_vector_store(session_id, vector_store)
    
    return {"session_id": session_id, "status": "success", "files_processed": len(files)}

@app.post("/v1/chat")
async def chat(message: str, session_id: str):
    vector_store = session_manager.get_vector_store(session_id)
    if not vector_store:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    
    result = await rag_service.get_answer(vector_store, message)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
