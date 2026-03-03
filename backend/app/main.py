from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import upload, chat, docs
from app.core.config import settings

app = FastAPI(title="DocuChat AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/v1", tags=["upload"])
app.include_router(chat.router, prefix="/v1", tags=["chat"])
app.include_router(docs.router, prefix="/v1", tags=["documents"])

@app.get("/")
async def root():
    return {"message": "DocuChat AI API is running"}
