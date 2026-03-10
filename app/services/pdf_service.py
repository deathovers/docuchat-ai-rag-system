import fitz  # PyMuPDF
from typing import List
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PDFService:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )

    def process_pdf(self, file_bytes: bytes, filename: str) -> List[Document]:
        """Extracts text from PDF and returns a list of chunked Documents with metadata."""
        documents = []
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text().strip()
                if not text:
                    continue
                
                # Create chunks for the page
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
