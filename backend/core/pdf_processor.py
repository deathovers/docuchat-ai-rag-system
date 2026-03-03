import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from typing import List

class PDFProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def process_pdf(self, file_path: str, file_name: str, session_id: str) -> List[Document]:
        """Extracts text from PDF and returns a list of LangChain Documents."""
        documents = []
        doc = fitz.open(file_path)
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if not text.strip():
                continue
                
            # Create chunks for this specific page
            chunks = self.text_splitter.split_text(text)
            
            for chunk in chunks:
                documents.append(Document(
                    page_content=chunk,
                    metadata={
                        "session_id": session_id,
                        "file_name": file_name,
                        "page_number": page_num + 1
                    }
                ))
        
        doc.close()
        return documents
