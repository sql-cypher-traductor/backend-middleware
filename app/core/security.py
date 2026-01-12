from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User, UserRole

# Configuración de seguridad Bearer Token
security = HTTPBearer()

# Instancia de Fernet para encriptación de datos sensibles
# Usa la SECRET_KEY del settings (debe ser de 32 bytes en base64)
_fernet = None


def get_fernet() -> Fernet:
    """Obtiene o crea la instancia de Fernet para encriptación."""
    global _fernet
    if _fernet is None:
        # Derivar una clave de 32 bytes desde la SECRET_KEY
        import base64
        import hashlib

        key_bytes = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        key_b64 = base64.urlsafe_b64encode(key_bytes)
        _fernet = Fernet(key_b64)
    return _fernet


def encrypt_data(data: str) -> str:
    """Encripta datos sensibles usando Fernet (AES-128).

    Args:
        data: Texto a encriptar

    Returns:
        Texto encriptado en base64
    """
    if not data:
        return ""
    fernet = get_fernet()
    encrypted = fernet.encrypt(data.encode("utf-8"))
    return encrypted.decode("utf-8")


def decrypt_data(encrypted_data: str) -> str:
    """Desencripta datos sensibles usando Fernet.

    Args:
        encrypted_data: Texto encriptado en base64

    Returns:
        Texto desencriptado

    Raises:
        ValueError: Si no se puede desencriptar
    """
    if not encrypted_data:
        return ""
    try:
        fernet = get_fernet()
        decrypted = fernet.decrypt(encrypted_data.encode("utf-8"))
        return decrypted.decode("utf-8")
    except Exception as e:
        raise ValueError(f"Error al desencriptar datos: {str(e)}") from e


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña coincide con su hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña usando bcrypt.

    Trunca la contraseña a 72 bytes para cumplir con el límite de bcrypt.
    """
    # Truncar a 72 bytes si es necesario (límite de bcrypt)
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    # Generar el hash con bcrypt
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def create_access_token(
    data: dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Crea un token JWT con los datos proporcionados.

    Args:
        data: Diccionario con los claims del token (user_id, role, etc.)
        expires_delta: Tiempo de expiración opcional.
            Por defecto usa ACCESS_TOKEN_EXPIRE_MINUTES

    Returns:
        Token JWT codificado como string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """Decodifica y valida un token JWT.

    Args:
        token: Token JWT a decodificar

    Returns:
        Diccionario con los claims del token o None si es inválido
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> User:
    """Obtiene el usuario actual desde el token JWT.

    Args:
        credentials: Credenciales HTTP Bearer
        db: Sesión de base de datos

    Returns:
        Usuario autenticado

    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo"
        )

    return user


def require_role(required_role: UserRole):
    """Dependencia para requerir un rol específico.

    Args:
        required_role: Rol requerido (ADMIN o DEV)

    Returns:
        Función de dependencia que valida el rol del usuario

    Raises:
        HTTPException: Si el usuario no tiene el rol requerido
    """

    def role_checker(
        current_user: User = Depends(get_current_user),  # noqa: B008
    ) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere rol {required_role.value}",
            )
        return current_user

    return role_checker


def require_admin(current_user: User = Depends(get_current_user)) -> User:  # noqa: B008
    """Dependencia para requerir rol ADMIN.

    Args:
        current_user: Usuario autenticado

    Returns:
        Usuario con rol ADMIN

    Raises:
        HTTPException: Si el usuario no es administrador
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador",
        )
    return current_user
