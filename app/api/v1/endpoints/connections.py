"""Endpoints para gestión de conexiones a bases de datos."""

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.connection import (
    ConnectionCreate,
    ConnectionResponse,
    ConnectionTestRequest,
    ConnectionTestResponse,
    ConnectionUpdate,
    DatabaseSchemaResponse,
)
from app.services.connection_service import ConnectionService

router = APIRouter()


@router.post(
    "/test",
    response_model=ConnectionTestResponse,
    status_code=status.HTTP_200_OK,
    summary="Probar conexión",
    description=(
        "Prueba la conectividad a una base de datos SQL Server o Neo4j "
        "sin guardar la configuración."
    ),
)
def test_connection(
    connection_data: ConnectionTestRequest,
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> ConnectionTestResponse:
    """Prueba una conexión a SQL Server o Neo4j.

    - **db_type**: Tipo de base de datos (sql_server o neo4j)
    - **host**: Dirección del servidor
    - **port**: Puerto del servidor
    - **db_user**: Usuario de la base de datos
    - **db_password**: Contraseña de la base de datos
    - **database_name**: Nombre de la BD (requerido solo para SQL Server)

    Returns:
        Resultado de la prueba con mensaje y tiempo de respuesta
    """
    return ConnectionService.test_connection(connection_data)


@router.post(
    "",
    response_model=ConnectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear conexión",
    description=(
        "Crea y guarda una nueva configuración de conexión. "
        "La contraseña se almacena encriptada."
    ),
)
def create_connection(
    connection_data: ConnectionCreate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> ConnectionResponse:
    """Crea una nueva conexión para el usuario autenticado.

    - **conn_name**: Nombre descriptivo de la conexión
    - **db_type**: Tipo de base de datos (sql_server o neo4j)
    - **host**: Dirección del servidor
    - **port**: Puerto del servidor
    - **db_user**: Usuario de la base de datos
    - **db_password**: Contraseña (se encripta automáticamente)
    - **database_name**: Nombre de la BD (requerido para SQL Server)

    Returns:
        Conexión creada (sin contraseña)
    """
    connection = ConnectionService.create_connection(
        db=db, user_id=current_user.user_id, connection_data=connection_data
    )

    # No incluir contraseña en la respuesta
    response = ConnectionResponse.model_validate(connection)
    return response


@router.get(
    "",
    response_model=List[ConnectionResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar conexiones",
    description="Obtiene todas las conexiones del usuario autenticado.",
)
def list_connections(
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> List[ConnectionResponse]:
    """Lista todas las conexiones del usuario autenticado.

    Returns:
        Lista de conexiones (sin contraseñas)
    """
    connections = ConnectionService.get_user_connections(db, current_user.user_id)

    # Convertir a schema de respuesta
    return [ConnectionResponse.model_validate(conn) for conn in connections]


@router.get(
    "/{connection_id}",
    response_model=ConnectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener conexión",
    description="Obtiene los detalles de una conexión específica.",
)
def get_connection(
    connection_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> ConnectionResponse:
    """Obtiene una conexión por su ID.

    Args:
        connection_id: ID de la conexión

    Returns:
        Detalles de la conexión (sin contraseña)

    Raises:
        404: Si la conexión no existe
        403: Si el usuario no es el propietario
    """
    connection = ConnectionService.get_connection(
        db, connection_id, current_user.user_id
    )
    return ConnectionResponse.model_validate(connection)


@router.put(
    "/{connection_id}",
    response_model=ConnectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar conexión",
    description="Actualiza los datos de una conexión existente.",
)
def update_connection(
    connection_id: int,
    connection_data: ConnectionUpdate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> ConnectionResponse:
    """Actualiza una conexión existente.

    Args:
        connection_id: ID de la conexión
        connection_data: Datos a actualizar (solo se actualizan los campos presentes)

    Returns:
        Conexión actualizada (sin contraseña)

    Raises:
        404: Si la conexión no existe
        403: Si el usuario no es el propietario
        400: Si los datos son inválidos
    """
    connection = ConnectionService.update_connection(
        db, connection_id, current_user.user_id, connection_data
    )
    return ConnectionResponse.model_validate(connection)


@router.delete(
    "/{connection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar conexión",
    description="Elimina permanentemente una conexión.",
)
def delete_connection(
    connection_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> None:
    """Elimina una conexión existente.

    Args:
        connection_id: ID de la conexión

    Raises:
        404: Si la conexión no existe
        403: Si el usuario no es el propietario
    """
    ConnectionService.delete_connection(db, connection_id, current_user.user_id)


@router.post(
    "/{connection_id}/test",
    response_model=ConnectionTestResponse,
    status_code=status.HTTP_200_OK,
    summary="Probar conexión existente",
    description=(
        "Prueba la conectividad de una conexión existente "
        "usando las credenciales almacenadas (encriptadas)."
    ),
)
def test_existing_connection(
    connection_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> ConnectionTestResponse:
    """Prueba una conexión existente sin necesidad de proporcionar credenciales.

    Usa la contraseña encriptada almacenada en la base de datos.

    Args:
        connection_id: ID de la conexión a probar

    Returns:
        Resultado de la prueba con mensaje y tiempo de respuesta

    Raises:
        404: Si la conexión no existe
        403: Si el usuario no es el propietario
    """
    return ConnectionService.test_existing_connection(
        db, connection_id, current_user.user_id
    )


@router.get(
    "/{connection_id}/schema",
    response_model=DatabaseSchemaResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener esquema de base de datos",
    description=(
        "Obtiene el esquema completo de una base de datos SQL Server, "
        "incluyendo tablas, columnas, tipos de datos y relaciones."
    ),
)
def get_database_schema(
    connection_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> DatabaseSchemaResponse:
    """Obtiene el esquema de la base de datos SQL Server conectada.

    Solo disponible para conexiones de tipo SQL Server.
    Incluye:
    - Lista de tablas con sus esquemas
    - Columnas con tipos de datos, PKs, FKs
    - Relaciones entre tablas

    Args:
        connection_id: ID de la conexión SQL Server

    Returns:
        Esquema completo de la base de datos

    Raises:
        404: Si la conexión no existe
        403: Si el usuario no es el propietario
        400: Si la conexión no es de tipo SQL Server
        500: Si hay error de conectividad
    """
    return ConnectionService.get_sql_server_schema(
        db, connection_id, current_user.user_id
    )
