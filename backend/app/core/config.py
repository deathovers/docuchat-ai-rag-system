from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "DocuChat AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    OPENAI_API_KEY: str
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
