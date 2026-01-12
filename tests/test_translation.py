"""
Pruebas unitarias para la funcionalidad de traducción SQL -> Cypher.

Cubre:
- Gramática ANTLR4 (T32)
- Visitor y mapeo de consultas (T33)
- Servicio de traducción con validaciones de seguridad (T33)
- Endpoint de traducción (T34)
- Persistencia de consultas en BD
- Casos de éxito y error
- Validaciones de seguridad
"""

import pytest

from app.core.parser.visitor import translate_sql_to_cypher
from app.models.query import Query, QueryStatus
from app.services.translation_service import TranslationService

# ============================================================================
# T32/T33: Tests de Visitor y Traducción Básica
# ============================================================================


def test_select_all_from_table():
    """T32: SELECT * FROM table básico."""
    sql = "SELECT * FROM Users"
    result = translate_sql_to_cypher(sql)

    assert result["success"] is True
    assert result["cypher"] == "MATCH (n:Users)\nRETURN n"
    assert result["errors"] == []


def test_select_specific_columns():
    """T32: SELECT con columnas específicas."""
    sql = "SELECT name, email FROM Users"
    result = translate_sql_to_cypher(sql)

    assert result["success"] is True
    assert result["cypher"] == "MATCH (n:Users)\nRETURN n.name, n.email"
    assert result["errors"] == []


def test_select_single_column():
    """T32: SELECT con una sola columna."""
    sql = "SELECT name FROM Products"
    result = translate_sql_to_cypher(sql)

    assert result["success"] is True
    assert result["cypher"] == "MATCH (n:Products)\nRETURN n.name"


def test_where_with_equal():
    """T33: WHERE con operador =."""
    sql = "SELECT * FROM Users WHERE age = 25"
    result = translate_sql_to_cypher(sql)

    assert result["success"] is True
    assert "MATCH (n:Users)" in result["cypher"]
    assert "WHERE n.age = 25" in result["cypher"]
    assert "RETURN n" in result["cypher"]


def test_where_with_greater_than():
    """T33: WHERE con operador >."""
    sql = "SELECT name FROM Users WHERE age > 18"
    result = translate_sql_to_cypher(sql)

    assert result["success"] is True
    assert "WHERE n.age > 18" in result["cypher"]
    assert "RETURN n.name" in result["cypher"]


def test_where_with_less_than():
    """T33: WHERE con operador <."""
    sql = "SELECT * FROM Products WHERE price < 100"
    result = translate_sql_to_cypher(sql)

    assert result["success"] is True
    assert "WHERE n.price < 100" in result["cypher"]


def test_where_with_not_equal():
    """T33: WHERE con operador !=."""
    sql = "SELECT * FROM Users WHERE status != 'inactive'"
    result = translate_sql_to_cypher(sql)

    assert result["success"] is True
    # En Cypher se usa <>
    assert "WHERE n.status <> 'inactive'" in result["cypher"]


def test_where_with_and():
    """T33: WHERE con operador AND."""
    sql = "SELECT * FROM Users WHERE age > 18 AND status = 'active'"
    result = translate_sql_to_cypher(sql)

    assert result["success"] is True
    assert "WHERE (n.age > 18 AND n.status = 'active')" in result["cypher"]


def test_where_with_or():
    """T33: WHERE con operador OR."""
    sql = "SELECT name FROM Users WHERE age < 18 OR role = 'guest'"
    result = translate_sql_to_cypher(sql)

    assert result["success"] is True
    assert "WHERE (n.age < 18 OR n.role = 'guest')" in result["cypher"]


def test_where_with_complex_condition():
    """T33: WHERE con condiciones complejas (AND y OR)."""
    sql = "SELECT * FROM Users WHERE (age > 18 AND status = 'active') OR role = 'admin'"
    result = translate_sql_to_cypher(sql)

    assert result["success"] is True
    assert result["cypher"] is not None


def test_where_with_string_value():
    """T33: WHERE con valor de cadena."""
    sql = "SELECT * FROM Users WHERE name = 'John'"
    result = translate_sql_to_cypher(sql)

    assert result["success"] is True
    assert "WHERE n.name = 'John'" in result["cypher"]


def test_where_with_boolean_true():
    """T33: WHERE con valor booleano true."""
    sql = "SELECT * FROM Users WHERE active = true"
    result = translate_sql_to_cypher(sql)

    assert result["success"] is True
    assert "WHERE n.active = true" in result["cypher"]


def test_where_with_null():
    """T33: WHERE con valor NULL."""
    sql = "SELECT * FROM Users WHERE last_login = null"
    result = translate_sql_to_cypher(sql)

    assert result["success"] is True
    assert "WHERE n.last_login = null" in result["cypher"]


def test_case_insensitive_keywords():
    """T32: Keywords case-insensitive."""
    sql = "select name from users where age > 18"
    result = translate_sql_to_cypher(sql)

    assert result["success"] is True
    assert result["cypher"] is not None


def test_invalid_syntax():
    """T32: Sintaxis SQL inválida."""
    sql = "SELECT FROM"
    result = translate_sql_to_cypher(sql)

    assert result["success"] is False
    assert result["cypher"] is None
    assert len(result["errors"]) > 0


# ============================================================================
# T33: Tests de TranslationService (Validaciones de Seguridad)
# ============================================================================


def test_service_validates_empty_query():
    """T33: Servicio rechaza consulta vacía."""
    result = TranslationService.translate("")

    assert result["success"] is False
    assert "no puede estar vacía" in result["errors"][0]


def test_service_validates_dangerous_keywords_drop():
    """T33: Servicio rechaza DROP."""
    result = TranslationService.translate("DROP TABLE Users")

    assert result["success"] is False
    assert "DROP" in result["errors"][0]


def test_service_validates_dangerous_keywords_delete():
    """T33: Servicio rechaza DELETE."""
    result = TranslationService.translate("DELETE FROM Users WHERE id = 1")

    assert result["success"] is False
    assert "DELETE" in result["errors"][0]


def test_service_validates_dangerous_keywords_update():
    """T33: Servicio rechaza UPDATE."""
    result = TranslationService.translate("UPDATE Users SET name = 'Test'")

    assert result["success"] is False
    assert "UPDATE" in result["errors"][0]


def test_service_validates_dangerous_keywords_insert():
    """T33: Servicio rechaza INSERT."""
    result = TranslationService.translate("INSERT INTO Users VALUES (1, 'Test')")

    assert result["success"] is False
    assert "INSERT" in result["errors"][0]


def test_service_validates_max_length():
    """T33: Servicio rechaza consultas muy largas."""
    long_query = "SELECT * FROM Users WHERE name = '" + ("A" * 6000) + "'"
    result = TranslationService.translate(long_query)

    assert result["success"] is False
    assert "excede el límite" in result["errors"][0]


def test_service_validates_only_select():
    """T33: Servicio solo acepta SELECT."""
    result = TranslationService.translate("CREATE TABLE Users (id INT)")

    assert result["success"] is False
    # El mensaje puede ser sobre CREATE o sobre que no es SELECT
    assert "CREATE" in result["errors"][0] or "SELECT" in result["errors"][0]


def test_service_detects_injection_pattern():
    """T33: Servicio detecta patrones de inyección SQL."""
    result = TranslationService.translate("SELECT * FROM Users; DROP TABLE Users")

    assert result["success"] is False
    # El mensaje puede incluir "sospechoso" o "DROP"
    error_msg = result["errors"][0].lower()
    assert "sospechoso" in error_msg or "drop" in error_msg


def test_service_successful_translation():
    """T33: Servicio realiza traducción exitosa."""
    result = TranslationService.translate("SELECT * FROM Users WHERE age > 18")

    assert result["success"] is True
    assert result["cypher"] is not None
    assert "MATCH (n:Users)" in result["cypher"]
    assert "translation_time" in result
    assert result["query_id"] is None  # Sin BD, no se guarda


def test_service_translation_with_time():
    """T33: Servicio mide tiempo de traducción."""
    result = TranslationService.translate("SELECT * FROM Users")

    assert result["success"] is True
    assert result["translation_time"] is not None
    assert result["translation_time"] >= 0


def test_service_get_examples():
    """T33: Servicio devuelve ejemplos."""
    examples = TranslationService.get_example_translations()

    assert len(examples) > 0
    assert all("sql" in ex for ex in examples)
    assert all("cypher" in ex for ex in examples)
    assert all("description" in ex for ex in examples)


# ============================================================================
# T34: Tests de Persistencia en BD
# ============================================================================


def test_translation_saves_to_database(db):
    """T34: Traducción guarda en BD con usuario."""
    from app.models.user import User

    # Crear usuario de prueba
    user = User(
        name="Test",
        last_name="User",
        email="translator_db@example.com",
        password="hashed_password",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Traducir con sesión y usuario
    result = TranslationService.translate(
        sql_query="SELECT * FROM Products",
        db=db,
        user_id=user.user_id,
    )

    assert result["success"] is True
    assert result["query_id"] is not None
    assert result["translation_time"] is not None

    # Verificar que se guardó en BD
    saved_query = db.query(Query).filter(Query.query_id == result["query_id"]).first()
    assert saved_query is not None
    assert saved_query.sql_query == "SELECT * FROM Products"
    assert saved_query.cypher_query is not None
    assert saved_query.status == QueryStatus.TRADUCIDO
    assert saved_query.user_id == user.user_id


def test_failed_translation_saves_to_database(db):
    """T34: Traducción fallida guarda error en BD."""
    from app.models.user import User

    user = User(
        name="Test",
        last_name="User",
        email="translator_fail@example.com",
        password="hashed_password",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    result = TranslationService.translate(
        sql_query="DROP TABLE Users",
        db=db,
        user_id=user.user_id,
    )

    assert result["success"] is False
    assert result["query_id"] is not None

    saved_query = db.query(Query).filter(Query.query_id == result["query_id"]).first()
    assert saved_query is not None
    assert saved_query.status == QueryStatus.FALLIDO
    assert saved_query.error_message is not None
    assert "DROP" in saved_query.error_message


def test_get_user_queries(db):
    """T34: Obtener historial de consultas de usuario."""
    from app.models.user import User

    user = User(
        name="Test",
        last_name="User",
        email="translator_history@example.com",
        password="hashed_password",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Crear varias traducciones
    for i in range(3):
        TranslationService.translate(
            sql_query=f"SELECT col{i} FROM Table{i}",
            db=db,
            user_id=user.user_id,
        )

    # Obtener historial
    queries = TranslationService.get_user_queries(
        db=db,
        user_id=user.user_id,
    )

    assert len(queries) == 3
    # Verificar orden descendente (más reciente primero)
    assert "col2" in queries[0].sql_query


# ============================================================================
# T34: Tests de Endpoint de Traducción
# ============================================================================


@pytest.fixture
def auth_token(client):
    """Fixture para obtener token de autenticación."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "translator@example.com",
            "password": "Test@2024!",
            "name": "Translator",
            "last_name": "User",
        },
    )
    return response.json()["access_token"]


def test_endpoint_translate_success(client, auth_token):
    """T34: Endpoint traduce consulta exitosamente."""
    response = client.post(
        "/api/v1/queries/translate",
        json={"sql_query": "SELECT * FROM Users WHERE age > 18"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["cypher"] is not None
    assert "MATCH (n:Users)" in data["cypher"]
    assert data["errors"] == []
    assert data["query_id"] is not None  # Ahora guarda en BD
    assert data["translation_time"] is not None


def test_endpoint_translate_with_specific_columns(client, auth_token):
    """T34: Endpoint traduce SELECT con columnas específicas."""
    response = client.post(
        "/api/v1/queries/translate",
        json={"sql_query": "SELECT name, email FROM Users"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "n.name, n.email" in data["cypher"]


def test_endpoint_translate_requires_auth(client):
    """T34: Endpoint requiere autenticación."""
    response = client.post(
        "/api/v1/queries/translate",
        json={"sql_query": "SELECT * FROM Users"},
    )

    assert response.status_code == 401


def test_endpoint_translate_invalid_query(client, auth_token):
    """T34: Endpoint rechaza consulta inválida."""
    response = client.post(
        "/api/v1/queries/translate",
        json={"sql_query": "DROP TABLE Users"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 400
    data = response.json()
    assert "DROP" in str(data)


def test_endpoint_translate_empty_query(client, auth_token):
    """T34: Endpoint rechaza consulta vacía."""
    response = client.post(
        "/api/v1/queries/translate",
        json={"sql_query": ""},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 422  # Validation error


def test_endpoint_translate_syntax_error(client, auth_token):
    """T34: Endpoint maneja errores de sintaxis."""
    response = client.post(
        "/api/v1/queries/translate",
        json={"sql_query": "SELECT FROM WHERE"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert len(data["errors"]) > 0


def test_endpoint_get_examples(client):
    """T34: Endpoint devuelve ejemplos (sin autenticación)."""
    response = client.get("/api/v1/queries/examples")

    assert response.status_code == 200
    data = response.json()
    assert "examples" in data
    assert len(data["examples"]) > 0

    first_example = data["examples"][0]
    assert "sql" in first_example
    assert "cypher" in first_example
    assert "description" in first_example


def test_endpoint_translate_complex_where(client, auth_token):
    """T34: Endpoint traduce WHERE complejo."""
    response = client.post(
        "/api/v1/queries/translate",
        json={
            "sql_query": "SELECT name FROM Users WHERE age > 18 AND status = 'active'"
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "AND" in data["cypher"]


def test_endpoint_history_requires_auth(client):
    """T34: Endpoint de historial requiere autenticación."""
    response = client.get("/api/v1/queries/history")
    assert response.status_code == 401


def test_endpoint_history_returns_user_queries(client, auth_token):
    """T34: Endpoint de historial devuelve consultas del usuario."""
    # Crear algunas traducciones
    for _ in range(2):
        client.post(
            "/api/v1/queries/translate",
            json={"sql_query": "SELECT * FROM Users"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

    # Obtener historial
    response = client.get(
        "/api/v1/queries/history",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

    # Verificar estructura
    first_query = data[0]
    assert "query_id" in first_query
    assert "sql_query" in first_query
    assert "cypher_query" in first_query
    assert "status" in first_query
    assert "created_at" in first_query
