import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import shutil
import uuid
from backend.core.rag_engine import RAGEngine

app = FastAPI(title="DocuChat AI API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Engine (API Key should be in env)
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

rag_engine = RAGEngine(api_key=GEMINI_API_KEY)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: str
    message: str
    history: List[ChatMessage]

@app.post("/upload")
async def upload_file(session_id: str = Form(...), file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    temp_dir = f"temp/{session_id}"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        await rag_engine.process_document(session_id, file_path, file.filename)
        return {"status": "success", "file_name": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Convert Pydantic models to dicts for the engine
        history_dicts = [{"role": m.role, "content": m.content} for m in request.history]
        
        response = await rag_engine.chat(
            session_id=request.session_id,
            message=request.message,
            history=history_dicts
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
