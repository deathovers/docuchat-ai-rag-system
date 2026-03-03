from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import VectorStoreService
from app.models.schemas import UploadResponse
from langchain.text_splitter import RecursiveCharacterTextSplitter

router = APIRouter()
vector_store = VectorStoreService()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

@router.post("/upload", response_model=UploadResponse)
async def upload_documents(
    session_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per session.")

    processed_filenames = []
    
    for file in files:
        if not file.filename.endswith(".pdf"):
            continue
            
        content = await file.read()
        try:
            pages_data = PDFProcessor.extract_text_with_metadata(content, file.filename)
            
            all_chunks = []
            all_metadatas = []
            
            for page in pages_data:
                chunks = text_splitter.split_text(page["text"])
                for chunk in chunks:
                    all_chunks.append(chunk)
                    all_metadatas.append(page["metadata"])
            
            vector_store.add_documents(all_chunks, all_metadatas, session_id)
            processed_filenames.append(file.filename)
            
        except ValueError as e:
            # Handle non-selectable text PDFs
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing {file.filename}: {str(e)}")

    return UploadResponse(
        filenames=processed_filenames,
        status="success",
        session_id=session_id
    )
