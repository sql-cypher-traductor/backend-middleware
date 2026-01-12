# Backend Middleware - SQL to Cypher Translator

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18.1-blue.svg)](https://www.postgresql.org/)
[![Neo4j](https://img.shields.io/badge/Neo4j-2025.11.2-brightgreen.svg)](https://neo4j.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)

## 📋 Descripción

Middleware backend desarrollado con FastAPI que actúa como intermediario entre bases de datos SQL (PostgreSQL, SQL Server) y bases de datos orientadas a grafos (Neo4j). El sistema traduce consultas SQL a Cypher utilizando ANTLR4 para el análisis sintáctico y semántico.

## 🏗️ Arquitectura

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│   Frontend  │─────▶│   Backend    │─────▶│  PostgreSQL  │
│  (Next.js)  │      │   (FastAPI)  │      │   Metadata   │
└─────────────┘      └──────────────┘      └──────────────┘
                            │
                            ├─────────────▶ SQL Server
                            │
                            └─────────────▶ Neo4j
```

### Componentes Principales

- **API REST**: Interfaz FastAPI con documentación automática (Swagger/OpenAPI)
- **Motor de Traducción**: Parser ANTLR4 para SQL → Cypher
- **Gestión de Conexiones**: Manejo dinámico de múltiples fuentes de datos
- **Servicio de Ejecución**: Ejecutor de consultas traducidas en Neo4j
- **Analytics**: Métricas y estadísticas de consultas y traducciones

## 🛠️ Stack Tecnológico

### Core
- **FastAPI**: Framework web asíncrono de alto rendimiento
- **Python 3.14**: Lenguaje base
- **Uvicorn**: Servidor ASGI con soporte para hot-reload

### Bases de Datos
- **PostgreSQL 18.1**: Almacenamiento de metadatos y configuraciones
- **SQL Server 2022**: Conexión a bases de datos SQL existentes
- **Neo4j 2025.11.2**: Base de datos de grafos destino

### ORM y Migraciones
- **SQLAlchemy**: ORM para gestión de bases de datos relacionales
- **Alembic**: Control de versiones y migraciones de esquema

### Parsing y Traducción
- **ANTLR4**: Generación de parsers para análisis léxico/sintáctico SQL
- **antlr4-python3-runtime**: Runtime para ejecución de parsers

### Calidad de Código
- **Ruff**: Linter de alto rendimiento
- **Black**: Formateador automático de código
- **Pytest**: Framework de testing

### Configuración
- **Pydantic Settings**: Validación y gestión de configuraciones
- **python-dotenv**: Carga de variables de entorno

## 📁 Estructura del Proyecto

```
backend-middleware/
├── alembic/                    # Migraciones de base de datos
│   ├── versions/              # Scripts de migración
│   └── env.py                 # Configuración de Alembic
├── app/
│   ├── api/v1/                # Endpoints API versión 1
│   │   ├── endpoints/
│   │   │   ├── analytics.py   # Métricas y estadísticas
│   │   │   ├── auth.py        # Autenticación y autorización
│   │   │   ├── connections.py # Gestión de conexiones
│   │   │   └── queries.py     # Ejecución de consultas
│   │   └── api.py             # Router principal
│   ├── core/
│   │   ├── config.py          # Configuración de la aplicación
│   │   ├── security.py        # JWT y seguridad
│   │   ├── exceptions.py      # Manejo de excepciones
│   │   └── parser/            # Parser ANTLR4
│   │       ├── grammar/       # Gramática SQL
│   │       ├── generated/     # Código generado por ANTLR
│   │       └── visitor.py     # Visitor para traducción
│   ├── db/
│   │   ├── base.py            # Base declarativa SQLAlchemy
│   │   └── session.py         # Sesiones de base de datos
│   ├── models/                # Modelos ORM
│   │   ├── user.py
│   │   ├── connection.py
│   │   └── query.py
│   ├── schemas/               # Schemas Pydantic
│   │   ├── user.py
│   │   └── query.py
│   ├── services/              # Lógica de negocio
│   │   ├── auth_service.py
│   │   ├── translation_service.py
│   │   └── execution_service.py
│   └── main.py                # Punto de entrada de la aplicación
├── tests/                     # Suite de pruebas
├── docker-compose.yml         # Orquestación de servicios
├── Dockerfile                 # Imagen Docker del backend
├── alembic.ini               # Configuración de Alembic
├── requirements.txt          # Dependencias Python
├── pyproject.toml            # Configuración del proyecto
└── .env                      # Variables de entorno (no versionado)
```

## 🚀 Inicio Rápido

### Prerequisitos

- Docker y Docker Compose
- Python 3.14+ (solo para desarrollo local)
- Git

### 1. Clonar el Repositorio

```bash
git clone https://github.com/sql-cypher-traductor/backend-middleware.git
cd backend-middleware
```

### 2. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# PostgreSQL
POSTGRES_USER=admin
POSTGRES_PASSWORD=P@ssw0rd
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=MiddlewareStatisticsDB

# SQL Server
SQL_SERVER_PASSWORD=P@ssw0rd

# Neo4j
NEO4J_PASSWORD=P@ssw0rd

# JWT
SECRET_KEY=tu_clave_secreta_muy_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

### 3. Levantar los Servicios con Docker

```bash
# Construir y levantar todos los contenedores
docker compose up -d --build

# Ver logs
docker compose logs -f

# Verificar estado
docker compose ps
```

### 4. Ejecutar Migraciones

```bash
# Dentro del contenedor del backend
docker exec -it translator_backend alembic upgrade head
```

### 5. Acceder a los Servicios

- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Frontend**: http://localhost:3000
- **Neo4j Browser**: http://localhost:7474
- **PostgreSQL**: localhost:5432
- **SQL Server**: localhost:1433

## 💻 Desarrollo Local

### Instalación de Dependencias

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecutar en Modo Desarrollo

```bash
# Con hot-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Linting y Formato

```bash
# Ejecutar linter
ruff check .

# Corregir automáticamente
ruff check --fix .

# Formatear código
black .
```

### Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=app tests/

# Tests específicos
pytest tests/test_translation_service.py
```

## 🗄️ Gestión de Base de Datos

### Crear Nueva Migración

```bash
# Generar migración automática
alembic revision --autogenerate -m "descripcion_del_cambio"

# Crear migración manual
alembic revision -m "descripcion_del_cambio"
```

### Aplicar Migraciones

```bash
# Migrar a la última versión
alembic upgrade head

# Migrar a versión específica
alembic upgrade <revision_id>

# Revertir última migración
alembic downgrade -1
```

### Ver Historial

```bash
# Historial de migraciones
alembic history

# Estado actual
alembic current
```

## 📡 API Endpoints

### Autenticación
- `POST /api/v1/auth/login` - Autenticación de usuario
- `POST /api/v1/auth/register` - Registro de usuario
- `POST /api/v1/auth/refresh` - Renovar token

### Conexiones
- `GET /api/v1/connections` - Listar conexiones
- `POST /api/v1/connections` - Crear conexión
- `PUT /api/v1/connections/{id}` - Actualizar conexión
- `DELETE /api/v1/connections/{id}` - Eliminar conexión
- `POST /api/v1/connections/{id}/test` - Probar conexión

### Consultas
- `POST /api/v1/queries/translate` - Traducir SQL a Cypher
- `POST /api/v1/queries/execute` - Ejecutar consulta traducida
- `GET /api/v1/queries/history` - Historial de consultas

### Analytics
- `GET /api/v1/analytics/stats` - Estadísticas generales
- `GET /api/v1/analytics/queries` - Análisis de consultas

## 🐳 Servicios Docker

### PostgreSQL
- **Imagen**: `postgres:18.1-alpine`
- **Puerto**: 5432
- **Uso**: Almacenamiento de metadatos, usuarios, conexiones

### SQL Server
- **Imagen**: `mcr.microsoft.com/mssql/server:2022-latest`
- **Puerto**: 1433
- **Uso**: Fuente de datos SQL para traducción

### Neo4j
- **Imagen**: `neo4j:2025.11.2-community`
- **Puertos**: 7474 (HTTP), 7687 (Bolt)
- **Uso**: Base de datos de grafos destino

### Backend
- **Build**: Dockerfile multi-stage
- **Puerto**: 8000
- **Volumen**: Hot-reload en desarrollo

### Frontend
- **Build**: Next.js standalone
- **Puerto**: 3000
- **Integración**: Comunicación con backend vía API REST

## 🔒 Seguridad

- Autenticación JWT con refresh tokens
- Passwords hasheados con bcrypt
- Variables de entorno para credenciales
- CORS configurado para orígenes permitidos
- Validación de entrada con Pydantic
- SQL injection prevention mediante ORM

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 👥 Equipo

Desarrollado por el equipo de SQL-Cypher Translator

## 📞 Contacto

Para consultas y soporte: [GitHub Issues](https://github.com/sql-cypher-traductor/backend-middleware/issues)