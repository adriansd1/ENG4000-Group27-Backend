import os
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List

load_dotenv()


class Settings(BaseModel):
    APP_NAME: str = "ENG400 Group27 Backend"
    POSTGRES_URL: str = os.getenv(
        "POSTGRES_URL",
        "postgresql://user:password@localhost:5432/PLC_db"
    )

    # Placeholder for later features
    OLLAMA_BASE_URL: str = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    )
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "phi3:mini")
    OLLAMA_TIMEOUT_SECONDS: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "800"))
    FRONTEND_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "FRONTEND_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000"
        ).split(",")
        if origin.strip()
    ]
    FEEDBACK_LOG_PATH: str = os.getenv(
        "FEEDBACK_LOG_PATH",
        "feedback/feedback_log.jsonl"  # planned for user feedback logging in later phase
    )

    # Knowledge Base Configuration Additions: 
    KB_DIR: str = os.getenv("KB_DIR", "knowledge_base")
    VECTOR_STORE_DIR: str = os.getenv("VECTOR_STORE_DIR", "vector_store")

    EMBED_MODEL: str = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

    KB_CHUNK_SIZE: int = int(os.getenv("KB_CHUNK_SIZE", "900"))
    KB_CHUNK_OVERLAP: int = int(os.getenv("KB_CHUNK_OVERLAP", "150"))

    KB_TOP_K: int = int(os.getenv("KB_TOP_K", "4"))
    SQL_DEFAULT_LIMIT: int = int(os.getenv("SQL_DEFAULT_LIMIT", "1000"))

    KB_ALLOWED_EXTENSIONS: List[str] = [".txt", ".md", ".pdf"]


settings = Settings()
