import fitz  # PyMuPDF
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
import io

class PDFService:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )

    def extract_documents(self, file_content: bytes, filename: str) -> List[Document]:
        documents = []
        doc = fitz.open(stream=file_content, filetype="pdf")
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                metadata = {
                    "file_name": filename,
                    "page_number": page_num + 1
                }
                # Split text into chunks while keeping metadata
                chunks = self.text_splitter.split_text(text)
                for chunk in chunks:
                    documents.append(Document(page_content=chunk, metadata=metadata))
        
        doc.close()
        return documents
