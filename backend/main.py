import os
import uuid
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain.schema import SystemMessage, HumanMessage

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

pc = Pinecone(api_key=PINECONE_API_KEY)

class ChatRequest(BaseModel):
    session_id: str
    message: str
    history: Optional[List[dict]] = []

@app.post("/upload")
async def upload_file(session_id: str = Form(...), file: UploadFile = File(...)):
    try:
        # 1. Read PDF
        content = await file.read()
        doc = fitz.open(stream=content, filetype="pdf")
        
        text_chunks = []
        metadatas = []
        
        # 2. Extract and Chunk
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            chunks = splitter.split_text(text)
            for chunk in chunks:
                text_chunks.append(chunk)
                metadatas.append({
                    "session_id": session_id,
                    "file_name": file.filename,
                    "page_number": page_num + 1
                })
        
        # 3. Embed and Upsert
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        index = pc.Index(PINECONE_INDEX_NAME)
        
        vector_store = PineconeVectorStore(index=index, embedding=embeddings, text_key="text")
        vector_store.add_texts(texts=text_chunks, metadatas=metadatas)
        
        return {"status": "success", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        index = pc.Index(PINECONE_INDEX_NAME)
        vector_store = PineconeVectorStore(index=index, embedding=embeddings, text_key="text")
        
        # Similarity Search with Session Filter
        docs = vector_store.similarity_search(
            request.message, 
            k=5, 
            filter={"session_id": {"$eq": request.session_id}}
        )

        context_parts = []
        sources = []
        for doc in docs:
            source_info = f"[{doc.metadata['file_name']} - Page {doc.metadata['page_number']}]"
            context_parts.append(f"Source {source_info}:\n{doc.page_content}")
            sources.append({"file_name": doc.metadata['file_name'], "page": doc.metadata['page_number']})

        context_text = "\n\n".join(context_parts)

        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
        
        system_prompt = (
            "You are a helpful assistant. Answer the user's question based ONLY on the provided context. "
            "If the answer is not in the context, state that it was not found. "
            "Cite your sources using [Filename - Page X] format at the end of relevant sentences."
        )
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Context:\n{context_text}\n\nQuestion: {request.message}")
        ]
        
        response = llm.invoke(messages)
        
        return {
            "answer": response.content,
            "sources": sources
        }
    except Exception as e:
        print(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/files/{session_id}")
async def clear_session(session_id: str):
    try:
        index = pc.Index(PINECONE_INDEX_NAME)
        index.delete(filter={"session_id": {"$eq": session_id}})
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
