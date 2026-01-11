from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Crear el motor de conexión
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,  # Si la conexión se cae, intenta reconectar
    echo=True,  # Muestra el SQL en la consola (útil para debug)
)

# Generar una sesión de conexión a la base de datos.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
