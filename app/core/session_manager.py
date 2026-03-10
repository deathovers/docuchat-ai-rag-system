from typing import Dict
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

class SessionManager:
    def __init__(self):
        # session_id -> FAISS index
        self.indices: Dict[str, FAISS] = {}

    def get_index(self, session_id: str) -> FAISS:
        return self.indices.get(session_id)

    def set_index(self, session_id: str, index: FAISS):
        self.indices[session_id] = index

    def add_to_index(self, session_id: str, index: FAISS):
        if session_id in self.indices:
            # FAISS merge or add
            self.indices[session_id].merge_from(index)
        else:
            self.indices[session_id] = index

    def clear_session(self, session_id: str):
        if session_id in self.indices:
            del self.indices[session_id]

session_manager = SessionManager()
