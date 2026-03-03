import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from typing import List
import io

class PDFService:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def process_pdf(self, file_content: bytes, filename: str) -> List[Document]:
        doc = fitz.open(stream=file_content, filetype="pdf")
        documents = []
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if not text.strip():
                continue
                
            chunks = self.text_splitter.split_text(text)
            for chunk in chunks:
                documents.append(Document(
                    page_content=chunk,
                    metadata={
                        "source": filename,
                        "page": page_num + 1
                    }
                ))
        
        return documents
