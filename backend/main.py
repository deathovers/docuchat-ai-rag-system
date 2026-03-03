from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from services.rag_service import RagService

app = FastAPI(title="DocuChat AI API")
rag_service = RagService()

class ChatRequest(BaseModel):
    session_id: str
    message: str
    history: Optional[List[dict]] = []

@app.post("/upload")
async def upload_document(session_id: str, file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    content = await file.read()
    await rag_service.process_document(session_id, file.filename, content)
    return {"message": f"Successfully processed {file.filename}", "session_id": session_id}

@app.post("/chat")
async def chat(request: ChatRequest):
    response = await rag_service.chat(request.session_id, request.message, request.history)
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
