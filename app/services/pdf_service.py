import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List
from app.core.config import settings

class PDFService:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )

    def process_pdf(self, file_bytes: bytes, filename: str) -> List[Document]:
        """Extracts text from PDF and splits into chunks with metadata."""
        documents = []
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text()
                if not text.strip():
                    continue
                
                chunks = self.text_splitter.split_text(text)
                for chunk in chunks:
                    documents.append(Document(
                        page_content=chunk,
                        metadata={
                            "file_name": filename,
                            "page_number": page_num
                        }
                    ))
        return documents
