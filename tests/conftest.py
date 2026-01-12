"""
Configuración compartida para pruebas con pytest.

Define fixtures y configuración común para todos los tests.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

# Base de datos en memoria para tests (compartida)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Crear engine y session DESPUÉS de importar Base con todos los modelos
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la dependencia de base de datos para tests."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Aplicar override de forma global
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """
    Crea las tablas antes de cada test y las elimina después.

    Se ejecuta automáticamente para cada función de test.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    """Proporciona una sesión de base de datos para tests que la necesiten."""
    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


@pytest.fixture(scope="module")
def client():
    """Cliente de pruebas de FastAPI."""
    return TestClient(app)


@pytest.fixture(scope="session")
def test_settings():
    """Configuración de prueba para toda la sesión."""
    return {
        "SECRET_KEY": "test_secret_key_for_testing_only",
        "ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
    }


def pytest_configure(config):
    """Configuración de pytest antes de ejecutar tests."""
    config.addinivalue_line("markers", "slow: marca tests que son lentos")
    config.addinivalue_line("markers", "integration: marca tests de integración")
    config.addinivalue_line("markers", "unit: marca tests unitarios")
