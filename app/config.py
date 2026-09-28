import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "ProcurePulse AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    DATABASE_URL: str = "sqlite:///./procurepulse.db"

    # LLM Settings
    LLM_PROVIDER: str = "mock"  # "mock" | "openai" | "anthropic" | "gemini"
    LLM_MODEL: str = "gpt-4o-mini"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # Guardrails & Business Constraints
    MAX_AUTO_APPROVE_AMOUNT: float = 5000.00
    MANAGER_APPROVAL_THRESHOLD: float = 25000.00
    MAX_PRICE_VARIANCE_PERCENT: float = 5.0
    SAFETY_STOCK_BUFFER_DAYS: int = 14
    DEFAULT_CURRENCY: str = "USD"

    # RAG Settings
    VECTOR_STORE_TYPE: str = "hybrid-memory"
    TOP_K_RETRIEVAL: int = 4
    SIMILARITY_THRESHOLD: float = 0.60

    # Workflow Settings
    HITL_AUTO_RESUME_ON_APPROVAL: bool = True
    COMPLIANCE_ENFORCEMENT_STRICT: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
