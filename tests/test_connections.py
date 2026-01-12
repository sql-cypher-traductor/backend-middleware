"""
Pruebas unitarias para los endpoints de conexiones.

Cubre:
- Creación de conexiones (CON-01)
- Prueba de conectividad (CON-01)
- Listar conexiones (CON-02)
- Actualizar conexiones (CON-02)
- Eliminar conexiones (CON-02)
- Seguridad y encriptación
- Validación de ownership
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.security import decrypt_data, encrypt_data
from app.main import app

client = TestClient(app)


@pytest.fixture
def auth_token():
    """Crea un usuario y retorna su token de autenticación."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "Test@2024!",
            "name": "Test",
            "last_name": "User",
        },
    )
    return response.json()["access_token"]


@pytest.fixture
def auth_token_second_user():
    """Crea un segundo usuario y retorna su token."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "seconduser@example.com",
            "password": "Test@2024!",
            "name": "Second",
            "last_name": "User",
        },
    )
    return response.json()["access_token"]


# ============================================================================
# CON-01: Tests de Creación y Prueba de Conexiones
# ============================================================================


@patch("app.services.connection_service.pyodbc.connect")
def test_test_sql_server_connection_success(mock_connect, auth_token):
    """T24: Prueba exitosa de conexión a SQL Server."""
    # Mock de la conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    response = client.post(
        "/api/v1/connections/test",
        json={
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "Password123!",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "exitosa" in data["message"].lower()
    assert "connection_time_ms" in data


@patch("app.services.connection_service.pyodbc.connect")
def test_test_sql_server_connection_failure(mock_connect, auth_token):
    """T24: Prueba fallida de conexión a SQL Server."""
    # Mock de error de conexión
    import pyodbc

    mock_connect.side_effect = pyodbc.Error("Login failed")

    response = client.post(
        "/api/v1/connections/test",
        json={
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "WrongPassword",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "connection_time_ms" in data


@patch("app.services.connection_service.GraphDatabase.driver")
def test_test_neo4j_connection_success(mock_driver, auth_token):
    """T24: Prueba exitosa de conexión a Neo4j."""
    # Mock de la conexión exitosa
    mock_driver_instance = MagicMock()
    mock_driver.return_value = mock_driver_instance

    response = client.post(
        "/api/v1/connections/test",
        json={
            "db_type": "neo4j",
            "host": "localhost",
            "port": 7687,
            "db_user": "neo4j",
            "db_password": "password",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "connection_time_ms" in data


def test_test_connection_requires_auth():
    """T24: Probar conexión requiere autenticación."""
    response = client.post(
        "/api/v1/connections/test",
        json={
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "Password123!",
            "database_name": "TestDB",
        },
    )

    assert response.status_code == 401  # 401 Unauthorized cuando no hay token


def test_test_sql_server_without_database_name(auth_token):
    """T24: SQL Server requiere database_name."""
    response = client.post(
        "/api/v1/connections/test",
        json={
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "Password123!",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 400  # Validation error desde el servicio


def test_create_sql_server_connection_success(auth_token):
    """T23, T25: Crear conexión SQL Server exitosamente."""
    response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "My SQL Server",
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "Password123!",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["conn_name"] == "My SQL Server"
    assert data["db_type"] == "sql_server"
    assert data["host"] == "localhost"
    assert data["port"] == 1433
    assert data["db_user"] == "sa"
    assert data["database_name"] == "TestDB"
    assert "db_password" not in data  # No debe exponerse
    assert "connection_id" in data
    assert "created_at" in data


def test_create_neo4j_connection_success(auth_token):
    """T23, T25: Crear conexión Neo4j exitosamente."""
    response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "My Neo4j",
            "db_type": "neo4j",
            "host": "localhost",
            "port": 7687,
            "db_user": "neo4j",
            "db_password": "neo4jpassword",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["conn_name"] == "My Neo4j"
    assert data["db_type"] == "neo4j"
    assert "db_password" not in data


def test_create_connection_duplicate_name(auth_token):
    """T23, T25: No permitir nombres duplicados para el mismo usuario."""
    # Primera conexión
    client.post(
        "/api/v1/connections",
        json={
            "conn_name": "Duplicate Name",
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "Password123!",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    # Intentar crear con el mismo nombre
    response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "Duplicate Name",
            "db_type": "neo4j",
            "host": "localhost",
            "port": 7687,
            "db_user": "neo4j",
            "db_password": "password",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 400
    assert "existe" in response.json()["detail"].lower()


def test_create_connection_requires_auth():
    """T23, T25: Crear conexión requiere autenticación."""
    response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "Test",
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "Password123!",
            "database_name": "TestDB",
        },
    )

    assert response.status_code == 401  # 401 Unauthorized cuando no hay token


def test_password_encryption_in_database(auth_token, db):
    """T23: Verificar que las contraseñas se encriptan en la BD."""
    # Crear conexión
    response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "Test Encryption",
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "PlainPassword123!",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 201

    # Verificar en la base de datos que la contraseña está encriptada
    from app.models.connection import Connection

    connection = db.query(Connection).first()

    # La contraseña almacenada no debe ser el texto plano
    assert connection.db_password != "PlainPassword123!"

    # Debe poder desencriptarse correctamente
    decrypted = decrypt_data(connection.db_password)
    assert decrypted == "PlainPassword123!"


# ============================================================================
# CON-02: Tests de Gestión de Conexiones
# ============================================================================


def test_list_connections_empty(auth_token):
    """T28: Listar conexiones cuando no hay ninguna."""
    response = client.get(
        "/api/v1/connections",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_list_connections_with_data(auth_token):
    """T28: Listar conexiones del usuario."""
    # Crear dos conexiones
    client.post(
        "/api/v1/connections",
        json={
            "conn_name": "Connection 1",
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "Password123!",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    client.post(
        "/api/v1/connections",
        json={
            "conn_name": "Connection 2",
            "db_type": "neo4j",
            "host": "localhost",
            "port": 7687,
            "db_user": "neo4j",
            "db_password": "password",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    # Listar conexiones
    response = client.get(
        "/api/v1/connections",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["conn_name"] == "Connection 1"
    assert data[1]["conn_name"] == "Connection 2"


def test_list_connections_only_own(auth_token, auth_token_second_user):
    """T28: Los usuarios solo ven sus propias conexiones."""
    # Usuario 1 crea una conexión
    client.post(
        "/api/v1/connections",
        json={
            "conn_name": "User 1 Connection",
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "Password123!",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    # Usuario 2 crea una conexión
    client.post(
        "/api/v1/connections",
        json={
            "conn_name": "User 2 Connection",
            "db_type": "neo4j",
            "host": "localhost",
            "port": 7687,
            "db_user": "neo4j",
            "db_password": "password",
        },
        headers={"Authorization": f"Bearer {auth_token_second_user}"},
    )

    # Usuario 1 lista sus conexiones
    response = client.get(
        "/api/v1/connections",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    data = response.json()
    assert len(data) == 1
    assert data[0]["conn_name"] == "User 1 Connection"


def test_get_connection_by_id(auth_token):
    """T28: Obtener una conexión específica por ID."""
    # Crear conexión
    create_response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "Test Connection",
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "Password123!",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    connection_id = create_response.json()["connection_id"]

    # Obtener conexión por ID
    response = client.get(
        f"/api/v1/connections/{connection_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["connection_id"] == connection_id
    assert data["conn_name"] == "Test Connection"


def test_get_connection_not_found(auth_token):
    """T28: Error 404 al buscar conexión inexistente."""
    response = client.get(
        "/api/v1/connections/99999",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 404


def test_get_connection_forbidden(auth_token, auth_token_second_user):
    """T28: Error 403 al intentar acceder a conexión de otro usuario."""
    # Usuario 1 crea conexión
    create_response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "User 1 Connection",
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "Password123!",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    connection_id = create_response.json()["connection_id"]

    # Usuario 2 intenta acceder
    response = client.get(
        f"/api/v1/connections/{connection_id}",
        headers={"Authorization": f"Bearer {auth_token_second_user}"},
    )

    assert response.status_code == 403


def test_update_connection_success(auth_token):
    """T29: Actualizar conexión exitosamente."""
    # Crear conexión
    create_response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "Original Name",
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "Password123!",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    connection_id = create_response.json()["connection_id"]

    # Actualizar conexión
    response = client.put(
        f"/api/v1/connections/{connection_id}",
        json={
            "conn_name": "Updated Name",
            "host": "newhost.com",
            "port": 1434,
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["conn_name"] == "Updated Name"
    assert data["host"] == "newhost.com"
    assert data["port"] == 1434
    # Campos no actualizados deben mantenerse
    assert data["db_user"] == "sa"


def test_update_connection_password_encryption(auth_token, db):
    """T29: Al actualizar contraseña, debe encriptarse."""
    # Crear conexión
    create_response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "Test",
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "OldPassword123!",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    connection_id = create_response.json()["connection_id"]

    # Actualizar contraseña
    response = client.put(
        f"/api/v1/connections/{connection_id}",
        json={"db_password": "NewPassword456!"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200

    # Verificar encriptación en BD
    from app.models.connection import Connection

    connection = (
        db.query(Connection).filter(Connection.connection_id == connection_id).first()
    )

    # La contraseña almacenada no debe ser el texto plano
    assert connection.db_password != "NewPassword456!"

    # Debe poder desencriptarse correctamente
    decrypted = decrypt_data(connection.db_password)
    assert decrypted == "NewPassword456!"


def test_update_connection_forbidden(auth_token, auth_token_second_user):
    """T29: Error 403 al intentar actualizar conexión de otro usuario."""
    # Usuario 1 crea conexión
    create_response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "User 1 Connection",
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "Password123!",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    connection_id = create_response.json()["connection_id"]

    # Usuario 2 intenta actualizar
    response = client.put(
        f"/api/v1/connections/{connection_id}",
        json={"conn_name": "Hacked"},
        headers={"Authorization": f"Bearer {auth_token_second_user}"},
    )

    assert response.status_code == 403


def test_delete_connection_success(auth_token):
    """T29: Eliminar conexión exitosamente."""
    # Crear conexión
    create_response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "To Delete",
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "Password123!",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    connection_id = create_response.json()["connection_id"]

    # Eliminar conexión
    response = client.delete(
        f"/api/v1/connections/{connection_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 204

    # Verificar que ya no existe
    get_response = client.get(
        f"/api/v1/connections/{connection_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert get_response.status_code == 404


def test_delete_connection_forbidden(auth_token, auth_token_second_user):
    """T29: Error 403 al intentar eliminar conexión de otro usuario."""
    # Usuario 1 crea conexión
    create_response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "User 1 Connection",
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "Password123!",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    connection_id = create_response.json()["connection_id"]

    # Usuario 2 intenta eliminar
    response = client.delete(
        f"/api/v1/connections/{connection_id}",
        headers={"Authorization": f"Bearer {auth_token_second_user}"},
    )

    assert response.status_code == 403


# ============================================================================
# Tests de Validación y Seguridad
# ============================================================================


def test_validation_host_with_dangerous_chars(auth_token):
    """Validar sanitización del campo host."""
    response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "Test",
            "db_type": "sql_server",
            "host": "localhost; DROP TABLE users;",
            "port": 1433,
            "db_user": "sa",
            "db_password": "Password123!",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 422


def test_validation_db_user_with_dangerous_chars(auth_token):
    """Validar sanitización del campo db_user."""
    response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "Test",
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa'; DROP TABLE users;--",
            "db_password": "Password123!",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 422


def test_validation_port_range(auth_token):
    """Validar rango de puerto."""
    response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "Test",
            "db_type": "sql_server",
            "host": "localhost",
            "port": 99999,  # Puerto inválido
            "db_user": "sa",
            "db_password": "Password123!",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 422


def test_encryption_decryption_cycle():
    """T23: Verificar ciclo completo de encriptación/desencriptación."""
    original_password = "MySecurePassword123!@#"

    # Encriptar
    encrypted = encrypt_data(original_password)

    # Verificar que es diferente al original
    assert encrypted != original_password

    # Desencriptar
    decrypted = decrypt_data(encrypted)

    # Verificar que el desencriptado es igual al original
    assert decrypted == original_password


# ============================================================================
# Tests de Prueba de Conexión Existente - CON-01 T24
# ============================================================================


@patch("app.services.connection_service.pyodbc.connect")
def test_test_existing_sql_server_connection_success(mock_connect, auth_token):
    """T24: Probar conexión SQL Server existente usando contraseña almacenada."""
    # Primero crear una conexión
    create_response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "Test SQL Existing",
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "StoredPassword123!",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    connection_id = create_response.json()["connection_id"]

    # Mock de la conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    # Probar la conexión existente (sin proporcionar contraseña)
    response = client.post(
        f"/api/v1/connections/{connection_id}/test",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "connection_time_ms" in data


@patch("app.services.connection_service.GraphDatabase.driver")
def test_test_existing_neo4j_connection_success(mock_driver, auth_token):
    """T24: Probar conexión Neo4j existente usando contraseña almacenada."""
    # Primero crear una conexión
    create_response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "Test Neo4j Existing",
            "db_type": "neo4j",
            "host": "localhost",
            "port": 7687,
            "db_user": "neo4j",
            "db_password": "StoredNeo4jPass!",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    connection_id = create_response.json()["connection_id"]

    # Mock de la conexión exitosa
    mock_driver_instance = MagicMock()
    mock_driver.return_value = mock_driver_instance

    # Probar la conexión existente
    response = client.post(
        f"/api/v1/connections/{connection_id}/test",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_test_existing_connection_not_found(auth_token):
    """T24: Error 404 al probar conexión inexistente."""
    response = client.post(
        "/api/v1/connections/99999/test",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 404


def test_test_existing_connection_forbidden(auth_token, auth_token_second_user):
    """T24: Error 403 al probar conexión de otro usuario."""
    # Usuario 1 crea conexión
    create_response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "User 1 Connection Test",
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "Password123!",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    connection_id = create_response.json()["connection_id"]

    # Usuario 2 intenta probar
    response = client.post(
        f"/api/v1/connections/{connection_id}/test",
        headers={"Authorization": f"Bearer {auth_token_second_user}"},
    )

    assert response.status_code == 403


def test_test_existing_connection_requires_auth():
    """T24: Probar conexión existente requiere autenticación."""
    response = client.post("/api/v1/connections/1/test")
    assert response.status_code == 401


# ============================================================================
# Tests de Obtener Esquema de Base de Datos - CON-01 Criterio de Aceptación
# ============================================================================


@patch("app.services.connection_service.pyodbc.connect")
def test_get_database_schema_success(mock_connect, auth_token):
    """CON-01: Obtener esquema de BD SQL Server exitosamente."""
    # Primero crear una conexión SQL Server
    create_response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "Schema Test SQL",
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "Password123!",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    connection_id = create_response.json()["connection_id"]

    # Mock de la conexión y consultas
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Mock de tablas
    mock_cursor.fetchall.side_effect = [
        # Tablas
        [("dbo", "Users", 100), ("dbo", "Orders", 500)],
        # Columnas
        [
            (
                "dbo",
                "Users",
                "user_id",
                "int",
                "NO",
                None,
                None,
                1,
                None,
                None,
            ),
            (
                "dbo",
                "Users",
                "email",
                "varchar",
                "NO",
                255,
                None,
                0,
                None,
                None,
            ),
            (
                "dbo",
                "Orders",
                "order_id",
                "int",
                "NO",
                None,
                None,
                1,
                None,
                None,
            ),
            (
                "dbo",
                "Orders",
                "user_id",
                "int",
                "NO",
                None,
                None,
                0,
                "Users",
                "user_id",
            ),
        ],
        # Relaciones
        [("FK_Orders_Users", "Orders", "user_id", "Users", "user_id")],
    ]

    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    # Obtener esquema
    response = client.get(
        f"/api/v1/connections/{connection_id}/schema",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["database_name"] == "TestDB"
    assert "tables" in data
    assert "relationships" in data
    assert "retrieved_at" in data
    assert len(data["tables"]) == 2
    assert len(data["relationships"]) == 1


def test_get_schema_neo4j_not_supported(auth_token):
    """CON-01: Obtener esquema no soportado para Neo4j."""
    # Crear conexión Neo4j
    create_response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "Schema Test Neo4j",
            "db_type": "neo4j",
            "host": "localhost",
            "port": 7687,
            "db_user": "neo4j",
            "db_password": "password",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    connection_id = create_response.json()["connection_id"]

    # Intentar obtener esquema
    response = client.get(
        f"/api/v1/connections/{connection_id}/schema",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 400
    assert "SQL Server" in response.json()["detail"]


def test_get_schema_not_found(auth_token):
    """CON-01: Error 404 al obtener esquema de conexión inexistente."""
    response = client.get(
        "/api/v1/connections/99999/schema",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 404


def test_get_schema_forbidden(auth_token, auth_token_second_user):
    """CON-01: Error 403 al obtener esquema de conexión de otro usuario."""
    # Usuario 1 crea conexión
    create_response = client.post(
        "/api/v1/connections",
        json={
            "conn_name": "User 1 Schema Test",
            "db_type": "sql_server",
            "host": "localhost",
            "port": 1433,
            "db_user": "sa",
            "db_password": "Password123!",
            "database_name": "TestDB",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    connection_id = create_response.json()["connection_id"]

    # Usuario 2 intenta obtener esquema
    response = client.get(
        f"/api/v1/connections/{connection_id}/schema",
        headers={"Authorization": f"Bearer {auth_token_second_user}"},
    )

    assert response.status_code == 403


def test_get_schema_requires_auth():
    """CON-01: Obtener esquema requiere autenticación."""
    response = client.get("/api/v1/connections/1/schema")
    assert response.status_code == 401
