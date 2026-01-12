"""Modelo de conexión a bases de datos SQL Server y Neo4j."""

import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class DatabaseType(str, enum.Enum):
    """Tipos de bases de datos soportados."""

    SQL_SERVER = "sql_server"
    NEO4J = "neo4j"


class Connection(Base):
    """Modelo de conexión a bases de datos externas.

    Almacena las configuraciones de conexión de los usuarios para SQL Server y Neo4j.
    Las contraseñas se almacenan encriptadas por seguridad.
    """

    __tablename__ = "connections"

    connection_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    conn_name = Column(String(100), nullable=False)
    db_type = Column(Enum(DatabaseType), nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    db_user = Column(String(255), nullable=False)
    db_password = Column(
        String(512), nullable=False
    )  # Encriptado, necesita más espacio
    database_name = Column(
        String(255), nullable=True
    )  # Para SQL Server, nombre de la BD
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relaciones
    user = relationship("User", backref="connections")
    queries = relationship("Query", back_populates="connection")

    def __repr__(self) -> str:
        return (
            f"<Connection(connection_id={self.connection_id}, "
            f"conn_name='{self.conn_name}', db_type='{self.db_type}')>"
        )
