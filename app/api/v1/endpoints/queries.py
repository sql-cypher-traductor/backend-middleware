"""
Endpoints para traducción de SQL a Cypher.

Proporciona endpoints para:
- Traducir consultas SQL a Cypher (QTE-01)
- Obtener ejemplos de traducción
- Consultar historial de traducciones
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.query import (
    QueryHistoryResponse,
    TranslateRequest,
    TranslateResponse,
    TranslationExample,
    TranslationExamplesResponse,
)
from app.services.translation_service import TranslationService

router = APIRouter()


@router.post(
    "/translate",
    response_model=TranslateResponse,
    status_code=status.HTTP_200_OK,
    summary="Traducir SQL a Cypher",
    description="""
    Traduce una consulta SQL SELECT a su equivalente en Cypher Neo4j.
    
    **Características soportadas:**
    - SELECT con columnas específicas o *
    - FROM con nombre de tabla
    - WHERE con operadores: =, !=, <, >, <=, >=
    - Operadores lógicos: AND, OR
    - Valores: strings, números, booleanos, null
    
    **Limitaciones:**
    - Solo consultas SELECT
    - No soporta JOIN, GROUP BY, ORDER BY, LIMIT
    - Una sola tabla por consulta
    
    **Seguridad:**
    - Requiere autenticación
    - Validación de entrada estricta
    - Protección contra inyección SQL
    """,
    responses={
        200: {
            "description": "Traducción exitosa",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "sql_query": "SELECT name FROM Users WHERE age > 18",
                        "cypher": "MATCH (n:Users)\nWHERE n.age > 18\nRETURN n.name",
                        "errors": [],
                    }
                }
            },
        },
        400: {
            "description": "Consulta SQL inválida",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "sql_query": "DROP TABLE Users",
                        "cypher": None,
                        "errors": [
                            "La consulta contiene la palabra clave no soportada: DROP"
                        ],
                    }
                }
            },
        },
        401: {"description": "No autenticado"},
        422: {"description": "Datos de entrada inválidos"},
    },
)
def translate_sql_to_cypher(
    request: TranslateRequest,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    """
    Traduce una consulta SQL a Cypher Neo4j.

    Args:
        request: Solicitud con la consulta SQL
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        TranslateResponse: Resultado de la traducción

    Raises:
        HTTPException: Si hay errores durante la traducción
    """
    # Realizar traducción y guardar en BD
    result = TranslationService.translate(
        sql_query=request.sql_query,
        db=db,
        user_id=current_user.user_id,
        neo4j_connection_id=request.neo4j_connection_id,
    )

    # Si la traducción falló por validación, retornar error 400
    if not result["success"]:
        # Si son errores de validación (palabras clave peligrosas, etc)
        if any(
            keyword in err
            for err in result["errors"]
            for keyword in [
                "no soportada",
                "no puede estar vacía",
                "excede el límite",
                "sospechoso",
            ]
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "sql_query": result["sql_query"],
                    "cypher": None,
                    "errors": result["errors"],
                    "query_id": result.get("query_id"),
                    "translation_time": result.get("translation_time"),
                },
            )

    # Retornar resultado (éxito o error de parsing)
    return TranslateResponse(
        success=result["success"],
        sql_query=result["sql_query"],
        cypher=result["cypher"],
        errors=result["errors"],
        query_id=result.get("query_id"),
        translation_time=result.get("translation_time"),
    )


@router.get(
    "/examples",
    response_model=TranslationExamplesResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener ejemplos de traducción",
    description="""
    Devuelve ejemplos de traducciones SQL -> Cypher.
    
    Útil para que el usuario aprenda la sintaxis soportada
    y vea casos de uso comunes.
    
    **No requiere autenticación** (endpoint público para documentación).
    """,
)
def get_translation_examples():
    """
    Obtiene ejemplos de traducción SQL -> Cypher.

    Returns:
        TranslationExamplesResponse: Lista de ejemplos
    """
    examples_data = TranslationService.get_example_translations()

    examples = [
        TranslationExample(
            sql=ex["sql"], cypher=ex["cypher"], description=ex["description"]
        )
        for ex in examples_data
    ]

    return TranslationExamplesResponse(examples=examples)


@router.get(
    "/history",
    response_model=List[QueryHistoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtener historial de traducciones",
    description="""
    Devuelve el historial de traducciones SQL -> Cypher del usuario autenticado.
    
    **Paginación:**
    - `skip`: Número de registros a omitir (por defecto 0)
    - `limit`: Número máximo de registros (por defecto 50, máximo 100)
    
    **Requiere autenticación.**
    """,
    responses={
        200: {
            "description": "Lista de traducciones del usuario",
        },
        401: {"description": "No autenticado"},
    },
)
def get_query_history(
    skip: int = Query(default=0, ge=0, description="Registros a omitir"),
    limit: int = Query(default=50, ge=1, le=100, description="Máximo de registros"),
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    """
    Obtiene el historial de traducciones del usuario.

    Args:
        skip: Número de registros a omitir
        limit: Número máximo de registros
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        List[QueryHistoryResponse]: Lista de traducciones
    """
    queries = TranslationService.get_user_queries(
        db=db,
        user_id=current_user.user_id,
        skip=skip,
        limit=limit,
    )

    return [
        QueryHistoryResponse(
            query_id=q.query_id,
            sql_query=q.sql_query,
            cypher_query=q.cypher_query,
            status=q.status.value,
            error_message=q.error_message,
            translation_time=q.translation_time,
            execution_time=q.execution_time,
            nodes_affected=q.nodes_affected,
            created_at=q.created_at,
            neo4j_connection_id=q.neo4j_connection_id,
        )
        for q in queries
    ]
