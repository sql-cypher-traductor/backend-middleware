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

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # Construye la URL de conexión a PostgreSQL: postgresql://user:pass@localhost:5432/db
        password_encoded = quote_plus(self.POSTGRES_PASSWORD)
        return f"postgresql://{self.POSTGRES_USER}:{password_encoded}@{self.POSTGRES_SERVER}:5432/{self.POSTGRES_DB}"


settings = Settings()
