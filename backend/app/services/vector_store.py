import os
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.docstore.document import Document

class VectorStoreService:
    def __init__(self, api_key: str):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", 
            google_api_key=api_key
        )
        self.storage_path = "storage/indices"
        os.makedirs(self.storage_path, exist_ok=True)

    def _get_index_path(self, session_id: str) -> str:
        return os.path.join(self.storage_path, f"{session_id}")

    def add_documents(self, session_id: str, documents: List[Document]):
        index_path = self._get_index_path(session_id)
        
        if os.path.exists(index_path):
            vectorstore = FAISS.load_local(
                index_path, self.embeddings, allow_dangerous_deserialization=True
            )
            vectorstore.add_documents(documents)
        else:
            vectorstore = FAISS.from_documents(documents, self.embeddings)
        
        vectorstore.save_local(index_path)

    def similarity_search(self, session_id: str, query: str, k: int = 5) -> List[Document]:
        index_path = self._get_index_path(session_id)
        if not os.path.exists(index_path):
            return []
        
        vectorstore = FAISS.load_local(
            index_path, self.embeddings, allow_dangerous_deserialization=True
        )
        return vectorstore.similarity_search(query, k=k)
