"""
Servicio de traducción de SQL a Cypher.

Gestiona la lógica de negocio para la traducción de consultas SQL a Cypher,
incluyendo validación, sanitización, logging y persistencia.
"""

import re
import time
from typing import Optional

from sqlalchemy.orm import Session

from app.core.parser.visitor import translate_sql_to_cypher
from app.models.query import Query, QueryStatus


class TranslationService:
    """
    Servicio para traducir consultas SQL a Cypher Neo4j.

    Implementa validaciones de seguridad y sanitización de entradas.
    """

    # Palabras clave SQL peligrosas (DDL/DML que no soportamos)
    DANGEROUS_KEYWORDS = [
        "DROP",
        "DELETE",
        "UPDATE",
        "INSERT",
        "CREATE",
        "ALTER",
        "TRUNCATE",
        "GRANT",
        "REVOKE",
        "EXEC",
        "EXECUTE",
    ]

    # Longitud máxima de consulta (protección contra DoS)
    MAX_QUERY_LENGTH = 5000

    @classmethod
    def validate_sql_query(cls, sql_query: str) -> dict:
        """
        Valida que la consulta SQL sea segura y soportada.

        Args:
            sql_query: Consulta SQL a validar

        Returns:
            dict: {'valid': bool, 'error': Optional[str]}
        """
        # Sanitizar entrada
        if not sql_query or not sql_query.strip():
            return {"valid": False, "error": "La consulta SQL no puede estar vacía"}

        # Verificar longitud máxima
        if len(sql_query) > cls.MAX_QUERY_LENGTH:
            return {
                "valid": False,
                "error": (
                    f"La consulta excede el límite de "
                    f"{cls.MAX_QUERY_LENGTH} caracteres"
                ),
            }

        # Convertir a mayúsculas para verificación
        sql_upper = sql_query.upper()

        # Verificar palabras clave peligrosas
        for keyword in cls.DANGEROUS_KEYWORDS:
            # Usar palabra completa con límites de palabra
            if re.search(rf"\b{keyword}\b", sql_upper):
                return {
                    "valid": False,
                    "error": (
                        f"La consulta contiene la palabra clave "
                        f"no soportada: {keyword}"
                    ),
                }

        # Verificar que sea un SELECT
        if not re.match(r"^\s*SELECT\b", sql_upper):
            return {
                "valid": False,
                "error": "Solo se soportan consultas SELECT",
            }

        # Validación de caracteres peligrosos (inyección)
        # Permitimos comillas simples para strings, pero detectamos patrones sospechosos
        if re.search(r";\s*(DROP|DELETE|UPDATE|INSERT)", sql_upper):
            return {
                "valid": False,
                "error": "Patrón de consulta sospechoso detectado",
            }

        return {"valid": True, "error": None}

    @classmethod
    def translate(
        cls,
        sql_query: str,
        db: Optional[Session] = None,
        user_id: Optional[int] = None,
        neo4j_connection_id: Optional[int] = None,
    ) -> dict:
        """
        Traduce una consulta SQL a Cypher y opcionalmente guarda en BD.

        Args:
            sql_query: Consulta SQL a traducir
            db: Sesión de base de datos (opcional, para persistir)
            user_id: ID del usuario (opcional, para persistir)
            neo4j_connection_id: ID de conexión Neo4j (opcional)

        Returns:
            dict: {
                'success': bool,
                'cypher': Optional[str],
                'errors': List[str],
                'sql_query': str,
                'query_id': Optional[int],
                'translation_time': Optional[float]
            }
        """
        # Sanitizar y normalizar entrada
        sql_query = sql_query.strip()

        # Validar consulta
        validation = cls.validate_sql_query(sql_query)
        if not validation["valid"]:
            # Si tenemos sesión de BD, guardar el intento fallido
            query_record = None
            if db and user_id:
                query_record = cls._save_query(
                    db=db,
                    user_id=user_id,
                    sql_query=sql_query,
                    cypher_query=None,
                    status=QueryStatus.FALLIDO,
                    error_message=validation["error"],
                    neo4j_connection_id=neo4j_connection_id,
                )

            return {
                "success": False,
                "cypher": None,
                "errors": [validation["error"]],
                "sql_query": sql_query,
                "query_id": query_record.query_id if query_record else None,
                "translation_time": None,
            }

        # Realizar traducción midiendo tiempo
        start_time = time.perf_counter()
        try:
            result = translate_sql_to_cypher(sql_query)
            end_time = time.perf_counter()
            translation_time_ms = (end_time - start_time) * 1000

            # Guardar en BD si tenemos sesión y usuario
            query_record = None
            if db and user_id:
                query_record = cls._save_query(
                    db=db,
                    user_id=user_id,
                    sql_query=sql_query,
                    cypher_query=result["cypher"],
                    status=(
                        QueryStatus.TRADUCIDO
                        if result["success"]
                        else QueryStatus.FALLIDO
                    ),
                    error_message=(result["errors"][0] if result["errors"] else None),
                    translation_time=translation_time_ms,
                    neo4j_connection_id=neo4j_connection_id,
                )

            return {
                "success": result["success"],
                "cypher": result["cypher"],
                "errors": result.get("errors", []),
                "sql_query": sql_query,
                "query_id": query_record.query_id if query_record else None,
                "translation_time": round(translation_time_ms, 3),
            }

        except Exception as e:
            end_time = time.perf_counter()
            translation_time_ms = (end_time - start_time) * 1000
            error_msg = f"Error inesperado durante la traducción: {str(e)}"

            # Guardar error en BD
            query_record = None
            if db and user_id:
                query_record = cls._save_query(
                    db=db,
                    user_id=user_id,
                    sql_query=sql_query,
                    cypher_query=None,
                    status=QueryStatus.FALLIDO,
                    error_message=error_msg,
                    translation_time=translation_time_ms,
                    neo4j_connection_id=neo4j_connection_id,
                )

            return {
                "success": False,
                "cypher": None,
                "errors": [error_msg],
                "sql_query": sql_query,
                "query_id": query_record.query_id if query_record else None,
                "translation_time": round(translation_time_ms, 3),
            }

    @classmethod
    def _save_query(
        cls,
        db: Session,
        user_id: int,
        sql_query: str,
        cypher_query: Optional[str],
        status: QueryStatus,
        error_message: Optional[str] = None,
        translation_time: Optional[float] = None,
        neo4j_connection_id: Optional[int] = None,
    ) -> Query:
        """
        Guarda un registro de consulta en la base de datos.

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            sql_query: Consulta SQL original
            cypher_query: Consulta Cypher traducida
            status: Estado de la consulta
            error_message: Mensaje de error si falló
            translation_time: Tiempo de traducción en ms
            neo4j_connection_id: ID de conexión Neo4j

        Returns:
            Query: Registro de consulta guardado
        """
        query = Query(
            user_id=user_id,
            sql_query=sql_query,
            cypher_query=cypher_query,
            status=status,
            error_message=error_message,
            translation_time=translation_time,
            neo4j_connection_id=neo4j_connection_id,
        )
        db.add(query)
        db.commit()
        db.refresh(query)
        return query

    @classmethod
    def get_user_queries(
        cls,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Query]:
        """
        Obtiene el historial de consultas de un usuario.

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver

        Returns:
            list[Query]: Lista de consultas del usuario
        """
        return (
            db.query(Query)
            .filter(Query.user_id == user_id)
            .order_by(Query.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @classmethod
    def get_example_translations(cls) -> list[dict]:
        """
        Devuelve ejemplos de traducciones SQL -> Cypher.

        Returns:
            list: Lista de diccionarios con ejemplos
        """
        return [
            {
                "sql": "SELECT * FROM Users",
                "cypher": "MATCH (n:Users)\nRETURN n",
                "description": "SELECT simple con todas las columnas",
            },
            {
                "sql": "SELECT name, email FROM Users",
                "cypher": "MATCH (n:Users)\nRETURN n.name, n.email",
                "description": "SELECT con columnas específicas",
            },
            {
                "sql": "SELECT name FROM Users WHERE age > 18",
                "cypher": "MATCH (n:Users)\nWHERE n.age > 18\nRETURN n.name",
                "description": "SELECT con WHERE y operador de comparación",
            },
            {
                "sql": "SELECT * FROM Users WHERE active = true AND role = 'admin'",
                "cypher": (
                    "MATCH (n:Users)\n"
                    "WHERE (n.active = true AND n.role = 'admin')\n"
                    "RETURN n"
                ),
                "description": "SELECT con WHERE y operador AND",
            },
            {
                "sql": "SELECT name FROM Users WHERE age < 18 OR status = 'guest'",
                "cypher": (
                    "MATCH (n:Users)\n"
                    "WHERE (n.age < 18 OR n.status = 'guest')\n"
                    "RETURN n.name"
                ),
                "description": "SELECT con WHERE y operador OR",
            },
        ]
