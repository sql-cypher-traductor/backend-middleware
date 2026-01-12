"""
Pruebas unitarias para los endpoints de autenticación.

Cubre:
- Registro de usuarios (AUM-01)
- Inicio de sesión (AUM-01)
- Obtención de perfil (AUM-01)
- Actualización de perfil (AUM-02)
- Flujo de olvido de contraseña (AUM-03)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.password_reset_token import PasswordResetToken

# Base de datos en memoria para tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

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


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Crea las tablas antes de cada test y las elimina después."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ============================================================================
# AUM-01: Tests de Registro e Inicio de Sesión
# ============================================================================


def test_register_user_success():
    """T01: Registro exitoso de un nuevo usuario."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "Test@2024!",
            "name": "Juan",
            "last_name": "Pérez",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["name"] == "Juan"
    assert data["user"]["last_name"] == "Pérez"
    assert data["user"]["role"] == "DEV"
    assert data["user"]["is_active"] is True


def test_register_user_duplicate_email():
    """T01: Intento de registro con email duplicado debe fallar."""
    # Primer registro
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "Test@2024!",
            "name": "User",
            "last_name": "One",
        },
    )

    # Segundo registro con mismo email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "Different@2024!",
            "name": "User",
            "last_name": "Two",
        },
    )

    assert response.status_code == 400
    assert "email ya está registrado" in response.json()["detail"]


def test_register_user_weak_password():
    """T03: Validación de contraseña débil."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "weak@example.com",
            "password": "weak",
            "name": "Test",
            "last_name": "User",
        },
    )

    assert response.status_code == 422


def test_register_user_invalid_email():
    """T03: Validación de formato de email inválido."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid-email",
            "password": "Test@2024!",
            "name": "Test",
            "last_name": "User",
        },
    )

    assert response.status_code == 422


def test_login_success():
    """T02: Login exitoso con credenciales válidas."""
    # Registrar usuario primero
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "Login@2024!",
            "name": "Login",
            "last_name": "Test",
        },
    )

    # Intentar login
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "Login@2024!"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "login@example.com"


def test_login_invalid_credentials():
    """T03: Login con contraseña incorrecta debe fallar."""
    # Registrar usuario
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "valid@example.com",
            "password": "Correct@2024!",
            "name": "User",
            "last_name": "Test",
        },
    )

    # Intentar login con contraseña incorrecta
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "valid@example.com", "password": "Wrong@2024!"},
    )

    assert response.status_code == 401
    assert "Credenciales inválidas" in response.json()["detail"]


def test_login_nonexistent_user():
    """T03: Login con usuario inexistente debe fallar."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "Test@2024!"},
    )

    assert response.status_code == 401


def test_login_missing_password():
    """T03: Login con campo password faltante debe retornar 422."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "missingpass@example.com"},
    )
    assert response.status_code == 422


def test_register_missing_last_name():
    """T03: Registro con campo last_name faltante debe retornar 422."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "missinglast@example.com",
            "password": "Test@2024!",
            "name": "OnlyName",
        },
    )
    assert response.status_code == 422


def test_register_password_min_length_boundary():
    """T03: Contraseña en el límite mínimo de longitud válida."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "minlen@example.com",
            "password": "Aa1!aaaa",  # 8 chars, cumple reglas
            "name": "Min",
            "last_name": "Len",
        },
    )
    assert response.status_code == 201
    assert response.json()["user"]["email"] == "minlen@example.com"


# ============================================================================
# AUM-01: Perfil del usuario
# ============================================================================


def test_get_current_user_authenticated():
    """T04: Obtener perfil de usuario autenticado."""
    # Registrar y obtener token
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "profile@example.com",
            "password": "Profile@2024!",
            "name": "Profile",
            "last_name": "User",
        },
    )
    token = register_response.json()["access_token"]

    # Obtener perfil
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "profile@example.com"
    assert data["name"] == "Profile"
    assert data["last_name"] == "User"
    assert "password" not in data


def test_get_current_user_unauthenticated():
    """T04: Acceso sin token debe fallar."""
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_get_current_user_invalid_token():
    """T04: Acceso con token inválido debe fallar."""
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401


def test_get_current_user_header_without_bearer_prefix():
    """T04: Header Authorization sin prefijo Bearer debe fallar."""
    # Registrar y obtener token
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "nobearer@example.com",
            "password": "NoBearer@2024!",
            "name": "No",
            "last_name": "Bearer",
        },
    )
    token = register_response.json()["access_token"]

    # Enviar token sin 'Bearer'
    response = client.get("/api/v1/auth/me", headers={"Authorization": token})
    assert response.status_code == 401


# ============================================================================
# AUM-02: Tests de Actualización de Perfil
# ============================================================================


def test_update_profile_name():
    """T09: Actualizar nombre de usuario."""
    # Registrar usuario
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "update@example.com",
            "password": "Update@2024!",
            "name": "Original",
            "last_name": "Name",
        },
    )
    token = register_response.json()["access_token"]

    # Actualizar perfil
    response = client.put(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Updated"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated"
    assert data["last_name"] == "Name"  # Sin cambios
    assert data["email"] == "update@example.com"  # Sin cambios


def test_update_profile_email():
    """T09: Actualizar email de usuario."""
    # Registrar usuario
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "oldemail@example.com",
            "password": "Email@2024!",
            "name": "User",
            "last_name": "Test",
        },
    )
    token = register_response.json()["access_token"]

    # Actualizar email
    response = client.put(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "newemail@example.com"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newemail@example.com"


def test_update_profile_duplicate_email():
    """T10: Actualizar a email ya existente debe fallar."""
    # Registrar dos usuarios
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "user1@example.com",
            "password": "User1@2024!",
            "name": "User",
            "last_name": "One",
        },
    )

    register_response2 = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user2@example.com",
            "password": "User2@2024!",
            "name": "User",
            "last_name": "Two",
        },
    )
    token2 = register_response2.json()["access_token"]

    # Intentar cambiar email de user2 a user1
    response = client.put(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token2}"},
        json={"email": "user1@example.com"},
    )

    assert response.status_code == 400
    assert "email ya está en uso" in response.json()["detail"]


def test_update_profile_partial():
    """T10: Actualización parcial de campos."""
    # Registrar usuario
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "partial@example.com",
            "password": "Partial@2024!",
            "name": "Original",
            "last_name": "LastName",
        },
    )
    token = register_response.json()["access_token"]

    # Actualizar solo last_name
    response = client.put(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"last_name": "Updated"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Original"  # Sin cambios
    assert data["last_name"] == "Updated"
    assert data["email"] == "partial@example.com"  # Sin cambios


def test_update_profile_all_fields():
    """T09: Actualizar todos los campos del perfil."""
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "allfields@example.com",
            "password": "AllFields@2024!",
            "name": "First",
            "last_name": "Last",
        },
    )
    token = register_response.json()["access_token"]

    response = client.put(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "NewName",
            "last_name": "NewLast",
            "email": "changed@example.com",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "NewName"
    assert data["last_name"] == "NewLast"
    assert data["email"] == "changed@example.com"


def test_update_profile_same_email_noop():
    """T10: Actualizar a mismo email debe ser permitido (sin cambio)."""
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "sameemail@example.com",
            "password": "SameEmail@2024!",
            "name": "User",
            "last_name": "Test",
        },
    )
    token = register_response.json()["access_token"]

    response = client.put(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "sameemail@example.com"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "sameemail@example.com"


def test_update_profile_invalid_email_format():
    """T10: Actualizar email con formato inválido debe retornar 422."""
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "badformatuser@example.com",
            "password": "BadFormat@2024!",
            "name": "Bad",
            "last_name": "Format",
        },
    )
    token = register_response.json()["access_token"]

    response = client.put(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "not-an-email"},
    )
    assert response.status_code == 422


def test_update_profile_unauthenticated():
    """T11: Actualización sin autenticación debe fallar."""
    response = client.put("/api/v1/auth/me", json={"name": "Hacker"})

    assert response.status_code == 401


# ============================================================================
# AUM-03: Tests de Restablecimiento de Contraseña
# ============================================================================


def test_forgot_password_existing_user():
    """T14: Solicitud de reset para usuario existente."""
    # Registrar usuario
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "forgot@example.com",
            "password": "Original@2024!",
            "name": "User",
            "last_name": "Test",
        },
    )

    # Solicitar reset
    response = client.post(
        "/api/v1/auth/forgot-password", json={"email": "forgot@example.com"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "email existe" in data["message"].lower()


def test_forgot_password_nonexistent_user():
    """T15: Solicitud de reset para usuario inexistente (no debe revelar)."""
    response = client.post(
        "/api/v1/auth/forgot-password", json={"email": "nonexistent@example.com"}
    )

    # Debe retornar mismo mensaje por seguridad
    assert response.status_code == 200
    data = response.json()
    assert "email existe" in data["message"].lower()


def test_forgot_password_invalid_email():
    """T15: Solicitud con email inválido."""
    response = client.post(
        "/api/v1/auth/forgot-password", json={"email": "invalid-email"}
    )

    assert response.status_code == 422


@pytest.mark.skip(reason="Requiere PostgreSQL con timezone awareness.")
def test_reset_password_with_valid_token():
    """T14: Reset de contraseña con token válido."""
    # Registrar usuario
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "reset@example.com",
            "password": "Original@2024!",
            "name": "User",
            "last_name": "Test",
        },
    )

    # Solicitar token
    client.post("/api/v1/auth/forgot-password", json={"email": "reset@example.com"})

    # Obtener token de la BD
    db = TestingSessionLocal()
    reset_token = db.query(PasswordResetToken).filter_by(user_id=1).first()

    if reset_token:
        # Hacer el token válido forzando expires_at a futuro
        from datetime import datetime, timedelta, timezone

        reset_token.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        db.commit()
        token = reset_token.token
    db.close()

    # Resetear contraseña
    response = client.post(
        f"/api/v1/auth/reset-password/{token}",
        json={
            "new_password": "NewPassword@2024!",
            "confirm_password": "NewPassword@2024!",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "restablecida exitosamente" in data["message"].lower()


def test_reset_password_invalid_token():
    """T14: Reset con token inválido debe fallar."""
    response = client.post(
        "/api/v1/auth/reset-password/invalid-token-12345",
        json={
            "new_password": "NewPassword@2024!",
            "confirm_password": "NewPassword@2024!",
        },
    )

    assert response.status_code == 400
    assert "inválido" in response.json()["detail"].lower()


def test_reset_password_mismatched_passwords():
    """T16: Validación de contraseñas que no coinciden."""
    response = client.post(
        "/api/v1/auth/reset-password/some-token",
        json={
            "new_password": "NewPassword@2024!",
            "confirm_password": "DifferentPassword@2024!",
        },
    )

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("no coinciden" in str(error).lower() for error in errors)


def test_reset_password_weak_password():
    """T16: Validación de contraseña débil en reset."""
    response = client.post(
        "/api/v1/auth/reset-password/some-token",
        json={"new_password": "weak", "confirm_password": "weak"},
    )

    assert response.status_code == 422


@pytest.mark.skip(reason="Requiere PostgreSQL con timezone awareness.")
def test_reset_password_token_used_twice():
    """T14: Token solo puede usarse una vez."""
    # Registrar usuario
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "oneuse@example.com",
            "password": "Original@2024!",
            "name": "User",
            "last_name": "Test",
        },
    )

    # Solicitar token
    client.post("/api/v1/auth/forgot-password", json={"email": "oneuse@example.com"})

    # Obtener token
    db = TestingSessionLocal()
    reset_token = db.query(PasswordResetToken).filter_by(user_id=1).first()

    if reset_token:
        # Hacer el token válido
        from datetime import datetime, timedelta, timezone

        reset_token.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        db.commit()
        token = reset_token.token
    db.close()

    # Primer reset (debe funcionar)
    response1 = client.post(
        f"/api/v1/auth/reset-password/{token}",
        json={
            "new_password": "FirstReset@2024!",
            "confirm_password": "FirstReset@2024!",
        },
    )
    assert response1.status_code == 200

    # Segundo reset con mismo token (debe fallar)
    response2 = client.post(
        f"/api/v1/auth/reset-password/{token}",
        json={
            "new_password": "SecondReset@2024!",
            "confirm_password": "SecondReset@2024!",
        },
    )
    assert response2.status_code == 400
    assert "ya usado" in response2.json()["detail"].lower()


@pytest.mark.skip(
    reason="Requiere PostgreSQL con timezone awareness. SQLite no soporta."
)
def test_login_after_password_reset():
    """T14: Login con nueva contraseña después de reset."""
    # Registrar usuario
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "loginafter@example.com",
            "password": "Original@2024!",
            "name": "User",
            "last_name": "Test",
        },
    )

    # Solicitar y resetear contraseña
    client.post(
        "/api/v1/auth/forgot-password", json={"email": "loginafter@example.com"}
    )

    db = TestingSessionLocal()
    reset_token = db.query(PasswordResetToken).filter_by(user_id=1).first()

    if reset_token:
        # Hacer el token válido
        from datetime import datetime, timedelta, timezone

        reset_token.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        db.commit()
        token = reset_token.token
    db.close()

    client.post(
        f"/api/v1/auth/reset-password/{token}",
        json={"new_password": "NewPass@2024!", "confirm_password": "NewPass@2024!"},
    )

    # Login con contraseña vieja debe fallar
    response_old = client.post(
        "/api/v1/auth/login",
        json={"email": "loginafter@example.com", "password": "Original@2024!"},
    )
    assert response_old.status_code == 401

    # Login con contraseña nueva debe funcionar
    response_new = client.post(
        "/api/v1/auth/login",
        json={"email": "loginafter@example.com", "password": "NewPass@2024!"},
    )
    assert response_new.status_code == 200
    assert "access_token" in response_new.json()


# ============================================================================
# Tests de Validaciones de Contraseña
# ============================================================================


def test_password_validation_no_uppercase():
    """T03/T16: Contraseña sin mayúsculas."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "noupper@example.com",
            "password": "lowercase123!",
            "name": "Test",
            "last_name": "User",
        },
    )

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("mayúscula" in str(error).lower() for error in errors)


def test_password_validation_no_lowercase():
    """T03/T16: Contraseña sin minúsculas."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "nolower@example.com",
            "password": "UPPERCASE123!",
            "name": "Test",
            "last_name": "User",
        },
    )

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("minúscula" in str(error).lower() for error in errors)


def test_password_validation_no_digit():
    """T03/T16: Contraseña sin números."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "nodigit@example.com",
            "password": "NoNumbers!",
            "name": "Test",
            "last_name": "User",
        },
    )

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("número" in str(error).lower() for error in errors)


def test_password_validation_no_special_char():
    """T03/T16: Contraseña sin caracteres especiales."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "nospecial@example.com",
            "password": "NoSpecial123",
            "name": "Test",
            "last_name": "User",
        },
    )

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("símbolo especial" in str(error).lower() for error in errors)


def test_password_validation_too_short():
    """T03/T16: Contraseña demasiado corta."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "short@example.com",
            "password": "Sh0rt!",
            "name": "Test",
            "last_name": "User",
        },
    )

    assert response.status_code == 422


def test_password_with_special_characters():
    """T03/T16: Contraseña con caracteres especiales extendidos (+, -, =, etc.)."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "special@example.com",
            "password": "Test+Pass=2024!",
            "name": "Special",
            "last_name": "User",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "special@example.com"


# ============================================================================
# Tests de Roles (Validación Adicional)
# ============================================================================


def test_default_role_is_dev():
    """Verificar que el rol por defecto es DEV."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "defaultrole@example.com",
            "password": "Test@2024!",
            "name": "Default",
            "last_name": "Role",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["user"]["role"] == "DEV"


def test_jwt_contains_role():
    """Verificar que el JWT contiene el claim de role."""
    from jose import jwt

    from app.core.config import settings

    # Registrar usuario
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "jwttest@example.com",
            "password": "Test@2024!",
            "name": "JWT",
            "last_name": "Test",
        },
    )

    token = register_response.json()["access_token"]

    # Decodificar token
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert "role" in payload
    assert payload["role"] == "DEV"
    assert "email" in payload
    assert payload["email"] == "jwttest@example.com"
