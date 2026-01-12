"""
Schemas Pydantic para operaciones de traducción y consultas.

Define estructuras de datos para:
- Solicitudes de traducción SQL -> Cypher
- Respuestas de traducción
- Ejemplos de traducción
- Historial de consultas
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class TranslateRequest(BaseModel):
    """
    Solicitud de traducción de SQL a Cypher.

    Attributes:
        sql_query: Consulta SQL a traducir
        neo4j_connection_id: ID de conexión Neo4j (opcional, para guardar en historial)
    """

    sql_query: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Consulta SQL a traducir a Cypher",
        json_schema_extra={"example": "SELECT * FROM Users WHERE age > 18"},
    )
    neo4j_connection_id: Optional[int] = Field(
        None,
        description="ID de conexión Neo4j para asociar con la traducción",
        json_schema_extra={"example": 1},
    )

    @field_validator("sql_query")
    @classmethod
    def validate_sql_query(cls, v: str) -> str:
        """
        Valida que la consulta no esté vacía después de sanitizar.

        Args:
            v: Valor del campo sql_query

        Returns:
            str: Valor sanitizado

        Raises:
            ValueError: Si la consulta está vacía después de sanitizar
        """
        if not v or not v.strip():
            raise ValueError("La consulta SQL no puede estar vacía")
        return v.strip()


class TranslateResponse(BaseModel):
    """
    Respuesta de traducción SQL a Cypher.

    Attributes:
        success: Indica si la traducción fue exitosa
        sql_query: Consulta SQL original
        cypher: Consulta Cypher traducida (None si falló)
        errors: Lista de errores encontrados durante la traducción
        query_id: ID del registro en BD (si se guardó)
        translation_time: Tiempo de traducción en milisegundos
    """

    success: bool = Field(..., description="Indica si la traducción fue exitosa")
    sql_query: str = Field(..., description="Consulta SQL original")
    cypher: Optional[str] = Field(
        None,
        description="Consulta Cypher traducida (null si hubo errores)",
        json_schema_extra={"example": "MATCH (n:Users)\nWHERE n.age > 18\nRETURN n"},
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Lista de errores encontrados durante la traducción",
    )
    query_id: Optional[int] = Field(None, description="ID del registro guardado en BD")
    translation_time: Optional[float] = Field(
        None, description="Tiempo de traducción en milisegundos"
    )


class QueryHistoryResponse(BaseModel):
    """
    Respuesta con historial de consulta guardada.

    Attributes:
        query_id: ID de la consulta
        sql_query: Consulta SQL
        cypher_query: Consulta Cypher traducida
        status: Estado de la consulta (traducido, ejecutado, fallido)
        error_message: Mensaje de error si falló
        translation_time: Tiempo de traducción en ms
        execution_time: Tiempo de ejecución en ms
        nodes_affected: Número de nodos afectados
        created_at: Fecha de creación
        neo4j_connection_id: ID de conexión Neo4j asociada
    """

    query_id: int
    sql_query: str
    cypher_query: Optional[str]
    status: str
    error_message: Optional[str] = None
    translation_time: Optional[float] = None
    execution_time: Optional[float] = None
    nodes_affected: Optional[int] = None
    created_at: datetime
    neo4j_connection_id: Optional[int] = None

    class Config:
        from_attributes = True


class TranslationExample(BaseModel):
    """
    Ejemplo de traducción SQL -> Cypher.

    Attributes:
        sql: Consulta SQL de ejemplo
        cypher: Consulta Cypher correspondiente
        description: Descripción del ejemplo
    """

    sql: str = Field(..., description="Consulta SQL de ejemplo")
    cypher: str = Field(..., description="Consulta Cypher correspondiente")
    description: str = Field(..., description="Descripción del ejemplo")


class TranslationExamplesResponse(BaseModel):
    """
    Respuesta con ejemplos de traducción.

    Attributes:
        examples: Lista de ejemplos de traducción
    """

    examples: List[TranslationExample] = Field(
        ..., description="Lista de ejemplos de traducción SQL -> Cypher"
    )
