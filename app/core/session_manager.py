from typing import Dict
from langchain_community.vectorstores import FAISS

class SessionManager:
    def __init__(self):
        # In-memory storage for FAISS indices keyed by session_id
        self.sessions: Dict[str, FAISS] = {}

    def set_vector_store(self, session_id: str, vector_store: FAISS):
        self.sessions[session_id] = vector_store

    def get_vector_store(self, session_id: str) -> FAISS:
        return self.sessions.get(session_id)

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

session_manager = SessionManager()
