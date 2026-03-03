import fitz  # PyMuPDF
from typing import List
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import settings

class PDFService:
    @staticmethod
    async def process_pdf(file_bytes: bytes, filename: str) -> List[Document]:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        documents = []
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            metadata = {
                "source": filename,
                "page": page_num + 1,
            }
            documents.append(Document(page_content=text, metadata=metadata))
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        return text_splitter.split_documents(documents)
