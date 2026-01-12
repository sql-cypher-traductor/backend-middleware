"""
Configuración compartida para pruebas con pytest.

Define fixtures y configuración común para todos los tests.
"""

import pytest


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
