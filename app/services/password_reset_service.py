"""
Servicio para gestionar el flujo de restablecimiento de contraseña.

Este módulo proporciona funcionalidad para:
- Generar tokens de restablecimiento de contraseña
- Validar tokens
- Restablecer contraseñas usando tokens
- Limpiar tokens expirados
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User


class PasswordResetService:
    """Servicio para gestionar tokens de restablecimiento de contraseña."""

    @staticmethod
    def create_reset_token(
        db: Session, email: str, expiration_minutes: int = 30
    ) -> Optional[str]:
        """
        Crea un token de restablecimiento de contraseña para un usuario.

        Args:
            db: Sesión de base de datos
            email: Email del usuario
            expiration_minutes: Minutos hasta que expire el token (default: 30)

        Returns:
            Token generado o None si el usuario no existe
        """
        # Buscar usuario por email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Por seguridad, no revelar si el email existe o no
            return None

        # Invalidar tokens anteriores del usuario que no hayan sido usados
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.user_id,
            PasswordResetToken.used == False,  # noqa: E712
        ).update({"used": True})

        # Generar nuevo token
        token = PasswordResetToken.generate_token()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expiration_minutes)

        # Crear registro en base de datos
        reset_token = PasswordResetToken(
            token=token,
            user_id=user.user_id,
            expires_at=expires_at,
        )
        db.add(reset_token)
        db.commit()

        return token

    @staticmethod
    def validate_reset_token(db: Session, token: str) -> Optional[PasswordResetToken]:
        """
        Valida un token de restablecimiento de contraseña.

        Args:
            db: Sesión de base de datos
            token: Token a validar

        Returns:
            PasswordResetToken si es válido, None si no existe o no es válido
        """
        reset_token = (
            db.query(PasswordResetToken)
            .filter(PasswordResetToken.token == token)
            .first()
        )

        if not reset_token:
            return None

        if not reset_token.is_valid():
            return None

        return reset_token

    @staticmethod
    def reset_password_with_token(db: Session, token: str, new_password: str) -> bool:
        """
        Restablece la contraseña de un usuario usando un token válido.

        Args:
            db: Sesión de base de datos
            token: Token de restablecimiento
            new_password: Nueva contraseña en texto plano

        Returns:
            True si se actualizó exitosamente, False si el token no es válido
        """
        # Validar token
        reset_token = PasswordResetService.validate_reset_token(db, token)
        if not reset_token:
            return False

        # Obtener usuario
        user = db.query(User).filter(User.user_id == reset_token.user_id).first()
        if not user:
            return False

        # Actualizar contraseña
        user.password = get_password_hash(new_password)

        # Marcar token como usado
        reset_token.used = True

        db.commit()
        return True

    @staticmethod
    def cleanup_expired_tokens(db: Session) -> int:
        """
        Elimina tokens expirados de la base de datos.

        Args:
            db: Sesión de base de datos

        Returns:
            Número de tokens eliminados
        """
        now = datetime.now(timezone.utc)
        deleted_count = (
            db.query(PasswordResetToken)
            .filter(PasswordResetToken.expires_at < now)
            .delete()
        )
        db.commit()
        return deleted_count
