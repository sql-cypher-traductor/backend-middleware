"""Excepciones personalizadas para la aplicación."""

from fastapi import HTTPException, status


class ValidationError(HTTPException):
    """Excepción para errores de validación de datos."""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class NotFoundError(HTTPException):
    """Excepción para recursos no encontrados."""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ForbiddenError(HTTPException):
    """Excepción para acceso prohibido."""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class UnauthorizedError(HTTPException):
    """Excepción para acceso no autorizado."""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class DatabaseConnectionError(HTTPException):
    """Excepción para errores de conexión a base de datos."""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


class ConflictError(HTTPException):
    """Excepción para conflictos de recursos."""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
