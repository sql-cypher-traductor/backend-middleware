from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# Importar modelos para registrarlos en la metadata de SQLAlchemy
# Este import es necesario para que Alembic detecte los modelos
from app.models import Connection, PasswordResetToken, Query, User  # noqa: F401

# Crear el motor de conexión
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,  # Si la conexión se cae, intenta reconectar
    echo=True,  # Muestra el SQL en la consola (útil para debug)
)

# Generar una sesión de conexión a la base de datos.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependencia para obtener sesión de base de datos.

    Yields:
        Sesión de SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
