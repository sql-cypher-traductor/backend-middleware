"""Schemas de validación para conexiones de bases de datos."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.connection import DatabaseType


class ConnectionBase(BaseModel):
    """Schema base para conexiones."""

    conn_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nombre descriptivo de la conexión",
    )
    db_type: DatabaseType = Field(..., description="Tipo de base de datos")
    host: str = Field(
        ..., min_length=1, max_length=255, description="Host del servidor"
    )
    port: int = Field(..., gt=0, lt=65536, description="Puerto del servidor")
    db_user: str = Field(
        ..., min_length=1, max_length=255, description="Usuario de la base de datos"
    )


class ConnectionCreate(ConnectionBase):
    """Schema para crear una nueva conexión."""

    db_password: str = Field(
        ..., min_length=1, max_length=255, description="Contraseña de la base de datos"
    )
    database_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Nombre de la base de datos (requerido para SQL Server)",
    )

    @field_validator("database_name")
    @classmethod
    def validate_database_name(cls, v: Optional[str], info) -> Optional[str]:
        """Valida que database_name esté presente para SQL Server."""
        # info.data contiene los valores ya validados
        if "db_type" in info.data:
            db_type = info.data["db_type"]
            if db_type == DatabaseType.SQL_SERVER and not v:
                raise ValueError(
                    "database_name es requerido para conexiones SQL Server"
                )
            if db_type == DatabaseType.NEO4J and v:
                raise ValueError("database_name no es válido para conexiones Neo4j")
        return v

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Sanitiza el host para prevenir inyección."""
        # Eliminar espacios en blanco
        v = v.strip()
        if not v:
            raise ValueError("El host no puede estar vacío")
        # Validar que no contenga caracteres peligrosos
        dangerous_chars = [";", "'", '"', "\\", "`", "$", "|", "&"]
        for char in dangerous_chars:
            if char in v:
                raise ValueError(f"El host contiene caracteres no permitidos: {char}")
        return v

    @field_validator("db_user")
    @classmethod
    def validate_db_user(cls, v: str) -> str:
        """Sanitiza el usuario para prevenir inyección."""
        v = v.strip()
        if not v:
            raise ValueError("El usuario no puede estar vacío")
        # Validar que no contenga caracteres peligrosos
        dangerous_chars = [";", "'", '"', "\\", "`", "$", "|", "&"]
        for char in dangerous_chars:
            if char in v:
                raise ValueError(
                    f"El usuario contiene caracteres no permitidos: {char}"
                )
        return v


class ConnectionUpdate(BaseModel):
    """Schema para actualizar una conexión existente."""

    conn_name: Optional[str] = Field(None, min_length=1, max_length=100)
    host: Optional[str] = Field(None, min_length=1, max_length=255)
    port: Optional[int] = Field(None, gt=0, lt=65536)
    db_user: Optional[str] = Field(None, min_length=1, max_length=255)
    db_password: Optional[str] = Field(None, min_length=1, max_length=255)
    database_name: Optional[str] = Field(None, max_length=255)

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: Optional[str]) -> Optional[str]:
        """Sanitiza el host si está presente."""
        if v is not None:
            v = v.strip()
            dangerous_chars = [";", "'", '"', "\\", "`", "$", "|", "&"]
            for char in dangerous_chars:
                if char in v:
                    raise ValueError(
                        f"El host contiene caracteres no permitidos: {char}"
                    )
        return v

    @field_validator("db_user")
    @classmethod
    def validate_db_user(cls, v: Optional[str]) -> Optional[str]:
        """Sanitiza el usuario si está presente."""
        if v is not None:
            v = v.strip()
            dangerous_chars = [";", "'", '"', "\\", "`", "$", "|", "&"]
            for char in dangerous_chars:
                if char in v:
                    raise ValueError(
                        f"El usuario contiene caracteres no permitidos: {char}"
                    )
        return v


class ConnectionResponse(ConnectionBase):
    """Schema para respuestas de conexión (sin contraseña)."""

    connection_id: int
    user_id: int
    database_name: Optional[str] = None
    created_at: datetime
    is_active: bool = Field(
        default=False,
        description="Indica si la conexión está activa (probada exitosamente)",
    )

    class Config:
        from_attributes = True


class ConnectionTestRequest(BaseModel):
    """Schema para probar una conexión."""

    db_type: DatabaseType
    host: str = Field(..., min_length=1, max_length=255)
    port: int = Field(..., gt=0, lt=65536)
    db_user: str = Field(..., min_length=1, max_length=255)
    db_password: str = Field(..., min_length=1, max_length=255)
    database_name: Optional[str] = Field(None, max_length=255)

    @field_validator("database_name")
    @classmethod
    def validate_database_name(cls, v: Optional[str], info) -> Optional[str]:
        """Valida que database_name esté presente para SQL Server."""
        if "db_type" in info.data:
            db_type = info.data["db_type"]
            if db_type == DatabaseType.SQL_SERVER and not v:
                raise ValueError(
                    "database_name es requerido para conexiones SQL Server"
                )
        return v


class ConnectionTestResponse(BaseModel):
    """Schema para respuesta de prueba de conexión."""

    success: bool = Field(..., description="Indica si la prueba fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo del resultado")
    connection_time_ms: Optional[float] = Field(
        None, description="Tiempo de conexión en milisegundos"
    )


# ============================================================================
# Schemas para Esquema de Base de Datos - CON-01 Criterio de Aceptación
# ============================================================================


class ColumnInfo(BaseModel):
    """Información de una columna de tabla SQL Server."""

    name: str = Field(..., description="Nombre de la columna")
    data_type: str = Field(..., description="Tipo de dato SQL")
    is_nullable: bool = Field(..., description="Si permite valores NULL")
    is_primary_key: bool = Field(
        default=False, description="Si es parte de la clave primaria"
    )
    is_foreign_key: bool = Field(default=False, description="Si es clave foránea")
    max_length: Optional[int] = Field(
        None, description="Longitud máxima para tipos de texto"
    )
    default_value: Optional[str] = Field(None, description="Valor por defecto")
    referenced_table: Optional[str] = Field(
        None, description="Tabla referenciada si es FK"
    )
    referenced_column: Optional[str] = Field(
        None, description="Columna referenciada si es FK"
    )


class TableInfo(BaseModel):
    """Información de una tabla SQL Server."""

    name: str = Field(..., description="Nombre de la tabla")
    schema_name: str = Field(default="dbo", description="Esquema de la tabla")
    columns: list[ColumnInfo] = Field(
        default_factory=list, description="Lista de columnas"
    )
    row_count: Optional[int] = Field(None, description="Número aproximado de filas")


class RelationshipInfo(BaseModel):
    """Información de una relación/FK entre tablas."""

    name: str = Field(..., description="Nombre de la restricción FK")
    source_table: str = Field(..., description="Tabla origen")
    source_column: str = Field(..., description="Columna origen")
    target_table: str = Field(..., description="Tabla destino")
    target_column: str = Field(..., description="Columna destino")


class DatabaseSchemaResponse(BaseModel):
    """Respuesta con el esquema completo de la base de datos SQL Server."""

    database_name: str = Field(..., description="Nombre de la base de datos")
    tables: list[TableInfo] = Field(default_factory=list, description="Lista de tablas")
    relationships: list[RelationshipInfo] = Field(
        default_factory=list, description="Lista de relaciones FK"
    )
    retrieved_at: datetime = Field(..., description="Fecha y hora de la consulta")
