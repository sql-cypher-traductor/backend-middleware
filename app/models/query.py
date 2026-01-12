"""
Modelo Query para almacenar historial de traducciones SQL->Cypher.

Registra cada traducción realizada por los usuarios, incluyendo métricas
de rendimiento y estados de ejecución.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class QueryStatus(str, enum.Enum):
    """Estados posibles de una consulta traducida."""

    TRADUCIDO = "traducido"
    EJECUTADO = "ejecutado"
    FALLIDO = "fallido"


class Query(Base):
    """
    Modelo para registrar traducciones SQL a Cypher.

    Almacena el historial completo de traducciones, incluyendo:
    - Consultas SQL y Cypher
    - Usuario y conexión Neo4j utilizados
    - Métricas de rendimiento (tiempos, nodos afectados)
    - Estado de ejecución y errores
    """

    __tablename__ = "queries"

    query_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    neo4j_connection_id = Column(
        Integer,
        ForeignKey("connections.connection_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Consultas
    sql_query = Column(Text, nullable=False)
    cypher_query = Column(Text, nullable=True)

    # Estado y errores
    status = Column(
        Enum(QueryStatus),
        nullable=False,
        default=QueryStatus.TRADUCIDO,
        index=True,
    )
    error_message = Column(Text, nullable=True)

    # Métricas de rendimiento
    translation_time = Column(
        Float,
        nullable=True,
        comment="Tiempo de traducción en milisegundos",
    )
    execution_time = Column(
        Float,
        nullable=True,
        comment="Tiempo de ejecución en milisegundos",
    )
    nodes_affected = Column(
        Integer,
        nullable=True,
        comment="Número de nodos afectados en la ejecución",
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    user = relationship("User", back_populates="queries")
    connection = relationship("Connection", back_populates="queries")

    def __repr__(self):
        return (
            f"<Query(query_id={self.query_id}, "
            f"user_id={self.user_id}, "
            f"status={self.status.value})>"
        )
