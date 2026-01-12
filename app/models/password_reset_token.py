import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class PasswordResetToken(Base):
    """Modelo para tokens de restablecimiento de contraseña de un solo uso."""

    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relación con User
    user = relationship("User", backref="reset_tokens")

    def __repr__(self) -> str:
        token_preview = self.token[:8] if self.token else "N/A"
        return (
            f"<PasswordResetToken(token='{token_preview}...', "
            f"user_id={self.user_id}, used={self.used})>"
        )

    @staticmethod
    def generate_token() -> str:
        """Genera un token UUID único para reset de contraseña."""
        return str(uuid.uuid4())

    def is_valid(self) -> bool:
        """Verifica si el token es válido (no usado y no expirado)."""
        now = datetime.now(timezone.utc)
        return not self.used and self.expires_at > now
