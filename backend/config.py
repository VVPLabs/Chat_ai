import os
from pathlib import Path
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


class Settings(BaseSettings):
    PROJECT_NAME: str = "Kairos"
    DEBUG: bool = True

    BASE_DIR: str = str(Path(__file__).resolve().parent)

    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    DB_URL: str = os.getenv("DB_URL", "")

    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: SecretStr = SecretStr(os.getenv("MAIL_PASSWORD", ""))
    MAIL_FROM: str = os.getenv("MAIL_FROM", "")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", ""))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "")
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    DOMAIN: str = os.getenv("DOMAIN", "")

    PINECONE_KEY: str = os.getenv("PINECONE_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")
    SERP_API_KEY: str = os.getenv("SERP_API_KEY", "")
    HYPERBROWSER_API_KEY: str = os.getenv("HYPERBROWSER_API_KEY", "")
    OPENWEATHERMAP_API_KEY: str = os.getenv("OPENWEATHERMAP_API_KEY", "")
    NEWSDATA_APIKEY: str = os.getenv("NEWSDATA_APIKEY", "")

    LANGSMITH_TRACING: str = os.getenv("LANGSMITH_TRACING", "")
    LANGSMITH_ENDPOINT: str = os.getenv("LANGSMITH_ENDPOINT", "")
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT", "")

    model_config = SettingsConfigDict(env_file=".env")

    if not JWT_SECRET:
        print(
            "⚠️ WARNING: JWT_SECRET is not set! Use a strong secret key in production."
        )


settings = Settings()
