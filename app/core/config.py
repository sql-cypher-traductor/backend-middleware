import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Cargar variables del archivo .env
load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "Middleware SQL-to-Graph"

    # IMPORTANTE: Aquí lee lo que pusiste en Docker
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")

    # JWT Configuration
    # HU AUM-01 T02: Token JWT con expiración de 24 horas por defecto (1440 minutos)
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")  # 24 horas por defecto
    )

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # Construye la URL de conexión a PostgreSQL: postgresql://user:pass@localhost:5432/db
        password_encoded = quote_plus(self.POSTGRES_PASSWORD)
        return f"postgresql://{self.POSTGRES_USER}:{password_encoded}@{self.POSTGRES_SERVER}:5432/{self.POSTGRES_DB}"


settings = Settings()
