from fastapi import APIRouter

from app.api.v1.endpoints import auth, connections, queries

api_router = APIRouter()

# Incluir routers de endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(
    connections.router, prefix="/connections", tags=["Conexiones"]
)
api_router.include_router(queries.router, prefix="/queries", tags=["Consultas"])
