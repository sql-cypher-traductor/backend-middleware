import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.sql import func

from app.db.base import Base


class UserRole(str, enum.Enum):
    """Roles de usuario en el sistema."""

    ADMIN = "ADMIN"
    DEV = "DEV"


class User(Base):
    """Modelo de usuario para autenticación y gestión de permisos."""

    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.DEV, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<User(user_id={self.user_id}, email='{self.email}', role='{self.role}')>"
        )
