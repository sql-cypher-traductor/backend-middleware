"""Servicio para gestionar conexiones a bases de datos externas."""

import logging
import time
from datetime import datetime, timezone
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
    ColumnInfo,
    ConnectionCreate,
    ConnectionTestRequest,
    ConnectionTestResponse,
    ConnectionUpdate,
    DatabaseSchemaResponse,
    RelationshipInfo,
    TableInfo,
)

logger = logging.getLogger(__name__)


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
        logger.info(
            f"Intentando conexión SQL Server: {host}:{port}/{database} como {user}"
        )

        try:
            # Construir cadena de conexión ODBC
            # Usar DRIVER={ODBC Driver 18 for SQL Server} instalado en Docker
            connection_string = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={host},{port};"
                f"DATABASE={database};"
                f"UID={user};"
                f"PWD={password};"
                f"TrustServerCertificate=yes;"
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
            # Log del error completo para diagnóstico
            logger.error(f"Error de conexión SQL Server: {error_msg}")
            # Sanitizar mensaje de error para no exponer información sensible
            safe_msg = "Error de conexión a SQL Server"
            if "login failed" in error_msg.lower():
                safe_msg = "Credenciales inválidas"
            elif (
                "server not found" in error_msg.lower()
                or "network" in error_msg.lower()
                or "could not open a connection" in error_msg.lower()
            ):
                # Sugerencia si está usando localhost
                if host.lower() in ("localhost", "127.0.0.1"):
                    safe_msg = (
                        "No se puede alcanzar el servidor. "
                        "Si estás en Docker, usa 'sqlserver_service' como host"
                    )
                else:
                    safe_msg = "No se puede alcanzar el servidor"
            elif "timeout" in error_msg.lower():
                safe_msg = "Tiempo de espera agotado"
            elif "driver" in error_msg.lower():
                safe_msg = "Driver ODBC no encontrado"

            return ConnectionTestResponse(
                success=False,
                message=safe_msg,
                connection_time_ms=round(elapsed_ms, 2),
            )
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Error inesperado en conexión SQL Server: {type(e).__name__}: {str(e)}"
            )
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

    @staticmethod
    def test_existing_connection(
        db: Session, connection_id: int, user_id: int
    ) -> ConnectionTestResponse:
        """Prueba una conexión existente usando la contraseña almacenada.

        Args:
            db: Sesión de base de datos
            connection_id: ID de la conexión a probar
            user_id: ID del usuario (para validar ownership)

        Returns:
            Resultado de la prueba de conexión

        Raises:
            NotFoundError: Si la conexión no existe
            ForbiddenError: Si el usuario no es el propietario
        """
        connection = ConnectionService.get_connection(db, connection_id, user_id)

        # Desencriptar la contraseña almacenada
        decrypted_password = ConnectionService.get_decrypted_password(connection)

        if connection.db_type == DatabaseType.SQL_SERVER:
            return ConnectionService.test_sql_server_connection(
                host=connection.host,
                port=connection.port,
                user=connection.db_user,
                password=decrypted_password,
                database=connection.database_name or "",
            )
        elif connection.db_type == DatabaseType.NEO4J:
            return ConnectionService.test_neo4j_connection(
                host=connection.host,
                port=connection.port,
                user=connection.db_user,
                password=decrypted_password,
            )
        else:
            raise ValidationError(
                f"Tipo de base de datos no soportado: {connection.db_type}"
            )

    @staticmethod
    def get_sql_server_schema(
        db: Session, connection_id: int, user_id: int
    ) -> DatabaseSchemaResponse:
        """Obtiene el esquema de una base de datos SQL Server.

        Incluye tablas, columnas, tipos de datos y relaciones FK.

        Args:
            db: Sesión de base de datos
            connection_id: ID de la conexión
            user_id: ID del usuario (para validar ownership)

        Returns:
            Esquema completo de la base de datos

        Raises:
            NotFoundError: Si la conexión no existe
            ForbiddenError: Si el usuario no es el propietario
            ValidationError: Si no es una conexión SQL Server
            DatabaseConnectionError: Si no se puede conectar
        """
        connection = ConnectionService.get_connection(db, connection_id, user_id)

        if connection.db_type != DatabaseType.SQL_SERVER:
            raise ValidationError(
                "Solo se puede obtener el esquema de conexiones SQL Server"
            )

        # Desencriptar la contraseña almacenada
        decrypted_password = ConnectionService.get_decrypted_password(connection)

        try:
            # Construir cadena de conexión
            connection_string = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={connection.host},{connection.port};"
                f"DATABASE={connection.database_name};"
                f"UID={connection.db_user};"
                f"PWD={decrypted_password};"
                f"TrustServerCertificate=yes;"
                f"Connection Timeout=10;"
            )

            conn = pyodbc.connect(connection_string, timeout=10)
            cursor = conn.cursor()

            # Obtener tablas
            tables_query = """
                SELECT 
                    t.TABLE_SCHEMA,
                    t.TABLE_NAME,
                    (SELECT SUM(p.rows) 
                     FROM sys.partitions p
                     JOIN sys.tables st ON p.object_id = st.object_id
                     WHERE st.name = t.TABLE_NAME 
                       AND p.index_id IN (0, 1)) as row_count
                FROM INFORMATION_SCHEMA.TABLES t
                WHERE t.TABLE_TYPE = 'BASE TABLE'
                ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME
            """
            cursor.execute(tables_query)
            tables_rows = cursor.fetchall()

            # Obtener columnas con información de PKs y FKs
            columns_query = """
                SELECT 
                    c.TABLE_SCHEMA,
                    c.TABLE_NAME,
                    c.COLUMN_NAME,
                    c.DATA_TYPE,
                    c.IS_NULLABLE,
                    c.CHARACTER_MAXIMUM_LENGTH,
                    c.COLUMN_DEFAULT,
                    CASE WHEN pk.COLUMN_NAME IS NOT NULL THEN 1 ELSE 0 END as is_pk,
                    fk.REFERENCED_TABLE_NAME,
                    fk.REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS c
                LEFT JOIN (
                    SELECT ku.TABLE_SCHEMA, ku.TABLE_NAME, ku.COLUMN_NAME
                    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                    JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE ku
                        ON tc.CONSTRAINT_NAME = ku.CONSTRAINT_NAME
                    WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
                ) pk ON c.TABLE_SCHEMA = pk.TABLE_SCHEMA 
                    AND c.TABLE_NAME = pk.TABLE_NAME 
                    AND c.COLUMN_NAME = pk.COLUMN_NAME
                LEFT JOIN (
                    SELECT 
                        cu.TABLE_SCHEMA,
                        cu.TABLE_NAME,
                        cu.COLUMN_NAME,
                        ku2.TABLE_NAME as REFERENCED_TABLE_NAME,
                        ku2.COLUMN_NAME as REFERENCED_COLUMN_NAME
                    FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
                    JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE cu
                        ON rc.CONSTRAINT_NAME = cu.CONSTRAINT_NAME
                    JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE ku2
                        ON rc.UNIQUE_CONSTRAINT_NAME = ku2.CONSTRAINT_NAME
                ) fk ON c.TABLE_SCHEMA = fk.TABLE_SCHEMA 
                    AND c.TABLE_NAME = fk.TABLE_NAME 
                    AND c.COLUMN_NAME = fk.COLUMN_NAME
                ORDER BY c.TABLE_SCHEMA, c.TABLE_NAME, c.ORDINAL_POSITION
            """
            cursor.execute(columns_query)
            columns_rows = cursor.fetchall()

            # Obtener relaciones (FKs)
            relationships_query = """
                SELECT 
                    rc.CONSTRAINT_NAME,
                    cu.TABLE_NAME as SOURCE_TABLE,
                    cu.COLUMN_NAME as SOURCE_COLUMN,
                    ku.TABLE_NAME as TARGET_TABLE,
                    ku.COLUMN_NAME as TARGET_COLUMN
                FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
                JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE cu
                    ON rc.CONSTRAINT_NAME = cu.CONSTRAINT_NAME
                JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE ku
                    ON rc.UNIQUE_CONSTRAINT_NAME = ku.CONSTRAINT_NAME
                ORDER BY rc.CONSTRAINT_NAME
            """
            cursor.execute(relationships_query)
            relationships_rows = cursor.fetchall()

            cursor.close()
            conn.close()

            # Procesar datos
            # Crear diccionario de columnas por tabla
            columns_by_table: dict = {}
            for row in columns_rows:
                table_key = f"{row[0]}.{row[1]}"  # schema.table
                if table_key not in columns_by_table:
                    columns_by_table[table_key] = []

                columns_by_table[table_key].append(
                    ColumnInfo(
                        name=row[2],
                        data_type=row[3],
                        is_nullable=row[4] == "YES",
                        max_length=row[5],
                        default_value=row[6],
                        is_primary_key=bool(row[7]),
                        is_foreign_key=row[8] is not None,
                        referenced_table=row[8],
                        referenced_column=row[9],
                    )
                )

            # Crear lista de tablas
            tables = []
            for row in tables_rows:
                table_key = f"{row[0]}.{row[1]}"
                tables.append(
                    TableInfo(
                        schema_name=row[0],
                        name=row[1],
                        row_count=row[2],
                        columns=columns_by_table.get(table_key, []),
                    )
                )

            # Crear lista de relaciones
            relationships = []
            for row in relationships_rows:
                relationships.append(
                    RelationshipInfo(
                        name=row[0],
                        source_table=row[1],
                        source_column=row[2],
                        target_table=row[3],
                        target_column=row[4],
                    )
                )

            return DatabaseSchemaResponse(
                database_name=connection.database_name or "",
                tables=tables,
                relationships=relationships,
                retrieved_at=datetime.now(timezone.utc),
            )

        except pyodbc.Error as e:
            error_msg = str(e).lower()
            safe_msg = "Error al obtener el esquema de la base de datos"
            if "login failed" in error_msg:
                safe_msg = "Credenciales inválidas"
            elif "server not found" in error_msg or "network" in error_msg:
                safe_msg = "No se puede alcanzar el servidor"
            elif "timeout" in error_msg:
                safe_msg = "Tiempo de espera agotado"

            raise DatabaseConnectionError(safe_msg) from e
        except Exception as e:
            raise DatabaseConnectionError(
                f"Error inesperado: {type(e).__name__}"
            ) from e
