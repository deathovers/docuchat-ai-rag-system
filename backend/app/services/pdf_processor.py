import fitz  # PyMuPDF
from typing import List, Dict, Any
import io

class PDFProcessor:
    @staticmethod
    def extract_text_with_metadata(file_content: bytes, filename: str) -> List[Dict[str, Any]]:
        doc = fitz.open(stream=file_content, filetype="pdf")
        pages_data = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            if not text.strip():
                continue
                
            pages_data.append({
                "text": text,
                "metadata": {
                    "filename": filename,
                    "page": page_num + 1
                }
            })
            
        doc.close()
        
        if not pages_data:
            raise ValueError(f"No extractable text found in {filename}. Scanned PDFs (OCR) are not supported.")
            
        return pages_data
