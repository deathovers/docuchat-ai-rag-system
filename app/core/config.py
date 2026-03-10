import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "DocuChat AI"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "your-key-here")
    MAX_FILES_PER_SESSION: int = 10
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 100

settings = Settings()
