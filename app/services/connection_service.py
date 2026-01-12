"""Servicio para gestionar conexiones a bases de datos externas."""

import time
from typing import List

import pyodbc
from neo4j import GraphDatabase
from sqlalchemy.orm import Session

from app.core.exceptions import (
    DatabaseConnectionError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.core.security import decrypt_data, encrypt_data
from app.models.connection import Connection, DatabaseType
from app.schemas.connection import (
    ConnectionCreate,
    ConnectionTestRequest,
    ConnectionTestResponse,
    ConnectionUpdate,
)


class ConnectionService:
    """Servicio para operaciones CRUD y pruebas de conexión."""

    @staticmethod
    def create_connection(
        db: Session, user_id: int, connection_data: ConnectionCreate
    ) -> Connection:
        """Crea una nueva conexión en la base de datos.

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario propietario
            connection_data: Datos de la conexión

        Returns:
            Conexión creada

        Raises:
            ValidationError: Si los datos son inválidos
        """
        # Validar que el nombre de la conexión no esté duplicado para este usuario
        existing = (
            db.query(Connection)
            .filter(
                Connection.user_id == user_id,
                Connection.conn_name == connection_data.conn_name,
            )
            .first()
        )
        if existing:
            raise ValidationError(
                f"Ya existe una conexión con el nombre '{connection_data.conn_name}'"
            )

        # Encriptar la contraseña antes de guardarla
        encrypted_password = encrypt_data(connection_data.db_password)

        # Crear nueva conexión
        db_connection = Connection(
            user_id=user_id,
            conn_name=connection_data.conn_name,
            db_type=connection_data.db_type,
            host=connection_data.host,
            port=connection_data.port,
            db_user=connection_data.db_user,
            db_password=encrypted_password,
            database_name=connection_data.database_name,
        )

        db.add(db_connection)
        db.commit()
        db.refresh(db_connection)

        return db_connection

    @staticmethod
    def get_connection(db: Session, connection_id: int, user_id: int) -> Connection:
        """Obtiene una conexión por ID.

        Args:
            db: Sesión de base de datos
            connection_id: ID de la conexión
            user_id: ID del usuario (para validar ownership)

        Returns:
            Conexión encontrada

        Raises:
            NotFoundError: Si la conexión no existe
            ForbiddenError: Si el usuario no es el propietario
        """
        connection = (
            db.query(Connection)
            .filter(Connection.connection_id == connection_id)
            .first()
        )

        if not connection:
            raise NotFoundError("Conexión no encontrada")

        if connection.user_id != user_id:
            raise ForbiddenError("No tienes permiso para acceder a esta conexión")

        return connection

    @staticmethod
    def get_user_connections(db: Session, user_id: int) -> List[Connection]:
        """Obtiene todas las conexiones de un usuario.

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario

        Returns:
            Lista de conexiones del usuario
        """
        return db.query(Connection).filter(Connection.user_id == user_id).all()

    @staticmethod
    def update_connection(
        db: Session,
        connection_id: int,
        user_id: int,
        connection_update: ConnectionUpdate,
    ) -> Connection:
        """Actualiza una conexión existente.

        Args:
            db: Sesión de base de datos
            connection_id: ID de la conexión
            user_id: ID del usuario (para validar ownership)
            connection_update: Datos a actualizar

        Returns:
            Conexión actualizada

        Raises:
            NotFoundError: Si la conexión no existe
            ForbiddenError: Si el usuario no es el propietario
            ValidationError: Si los datos son inválidos
        """
        connection = ConnectionService.get_connection(db, connection_id, user_id)

        # Actualizar campos si están presentes
        update_data = connection_update.model_dump(exclude_unset=True)

        # Si se actualiza el nombre, validar que no esté duplicado
        if "conn_name" in update_data:
            existing = (
                db.query(Connection)
                .filter(
                    Connection.user_id == user_id,
                    Connection.conn_name == update_data["conn_name"],
                    Connection.connection_id != connection_id,
                )
                .first()
            )
            if existing:
                raise ValidationError(
                    f"Ya existe una conexión con el nombre '{update_data['conn_name']}'"
                )

        # Si se actualiza la contraseña, encriptarla
        if "db_password" in update_data:
            update_data["db_password"] = encrypt_data(update_data["db_password"])

        # Aplicar actualizaciones
        for field, value in update_data.items():
            setattr(connection, field, value)

        db.commit()
        db.refresh(connection)

        return connection

    @staticmethod
    def delete_connection(db: Session, connection_id: int, user_id: int) -> None:
        """Elimina una conexión.

        Args:
            db: Sesión de base de datos
            connection_id: ID de la conexión
            user_id: ID del usuario (para validar ownership)

        Raises:
            NotFoundError: Si la conexión no existe
            ForbiddenError: Si el usuario no es el propietario
        """
        connection = ConnectionService.get_connection(db, connection_id, user_id)
        db.delete(connection)
        db.commit()

    @staticmethod
    def test_sql_server_connection(
        host: str, port: int, user: str, password: str, database: str
    ) -> ConnectionTestResponse:
        """Prueba una conexión a SQL Server.

        Args:
            host: Host del servidor
            port: Puerto del servidor
            user: Usuario de la base de datos
            password: Contraseña de la base de datos
            database: Nombre de la base de datos

        Returns:
            Resultado de la prueba de conexión
        """
        start_time = time.time()

        try:
            # Construir cadena de conexión ODBC
            # Usar DRIVER={ODBC Driver 17 for SQL Server} o el disponible
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={host},{port};"
                f"DATABASE={database};"
                f"UID={user};"
                f"PWD={password};"
                f"Connection Timeout=5;"
            )

            # Intentar conexión
            conn = pyodbc.connect(connection_string, timeout=5)
            cursor = conn.cursor()

            # Ejecutar una consulta simple para verificar
            cursor.execute("SELECT 1")
            cursor.fetchone()

            # Cerrar conexión
            cursor.close()
            conn.close()

            elapsed_ms = (time.time() - start_time) * 1000

            return ConnectionTestResponse(
                success=True,
                message="Conexión exitosa a SQL Server",
                connection_time_ms=round(elapsed_ms, 2),
            )

        except pyodbc.Error as e:
            elapsed_ms = (time.time() - start_time) * 1000
            error_msg = str(e)
            # Sanitizar mensaje de error para no exponer información sensible
            safe_msg = "Error de conexión a SQL Server"
            if "login failed" in error_msg.lower():
                safe_msg = "Credenciales inválidas"
            elif (
                "server not found" in error_msg.lower()
                or "network" in error_msg.lower()
            ):
                safe_msg = "No se puede alcanzar el servidor"
            elif "timeout" in error_msg.lower():
                safe_msg = "Tiempo de espera agotado"

            return ConnectionTestResponse(
                success=False,
                message=safe_msg,
                connection_time_ms=round(elapsed_ms, 2),
            )
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            return ConnectionTestResponse(
                success=False,
                message=f"Error inesperado: {type(e).__name__}",
                connection_time_ms=round(elapsed_ms, 2),
            )

    @staticmethod
    def test_neo4j_connection(
        host: str, port: int, user: str, password: str
    ) -> ConnectionTestResponse:
        """Prueba una conexión a Neo4j.

        Args:
            host: Host del servidor
            port: Puerto del servidor
            user: Usuario de la base de datos
            password: Contraseña de la base de datos

        Returns:
            Resultado de la prueba de conexión
        """
        start_time = time.time()

        try:
            # Construir URI de conexión (bolt://host:port)
            uri = f"bolt://{host}:{port}"

            # Crear driver con timeout
            driver = GraphDatabase.driver(
                uri,
                auth=(user, password),
                connection_timeout=5,
                max_connection_lifetime=5,
            )

            # Verificar conectividad
            driver.verify_connectivity()

            # Cerrar driver
            driver.close()

            elapsed_ms = (time.time() - start_time) * 1000

            return ConnectionTestResponse(
                success=True,
                message="Conexión exitosa a Neo4j",
                connection_time_ms=round(elapsed_ms, 2),
            )

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            error_msg = str(e).lower()

            # Sanitizar mensaje de error
            safe_msg = "Error de conexión a Neo4j"
            if "authentication" in error_msg or "unauthorized" in error_msg:
                safe_msg = "Credenciales inválidas"
            elif "connection refused" in error_msg or "cannot connect" in error_msg:
                safe_msg = "No se puede alcanzar el servidor"
            elif "timeout" in error_msg:
                safe_msg = "Tiempo de espera agotado"

            return ConnectionTestResponse(
                success=False,
                message=safe_msg,
                connection_time_ms=round(elapsed_ms, 2),
            )

    @staticmethod
    def test_connection(
        connection_data: ConnectionTestRequest,
    ) -> ConnectionTestResponse:
        """Prueba una conexión según su tipo.

        Args:
            connection_data: Datos de conexión a probar

        Returns:
            Resultado de la prueba

        Raises:
            ValidationError: Si el tipo de base de datos no es soportado
        """
        if connection_data.db_type == DatabaseType.SQL_SERVER:
            if not connection_data.database_name:
                raise ValidationError("database_name es requerido para SQL Server")

            return ConnectionService.test_sql_server_connection(
                host=connection_data.host,
                port=connection_data.port,
                user=connection_data.db_user,
                password=connection_data.db_password,
                database=connection_data.database_name,
            )

        elif connection_data.db_type == DatabaseType.NEO4J:
            return ConnectionService.test_neo4j_connection(
                host=connection_data.host,
                port=connection_data.port,
                user=connection_data.db_user,
                password=connection_data.db_password,
            )

        else:
            raise ValidationError(
                f"Tipo de base de datos no soportado: {connection_data.db_type}"
            )

    @staticmethod
    def get_decrypted_password(connection: Connection) -> str:
        """Obtiene la contraseña desencriptada de una conexión.

        Args:
            connection: Objeto Connection

        Returns:
            Contraseña desencriptada

        Raises:
            DatabaseConnectionError: Si no se puede desencriptar
        """
        try:
            return decrypt_data(connection.db_password)
        except Exception as e:
            raise DatabaseConnectionError(
                f"Error al obtener contraseña: {str(e)}"
            ) from e
