import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole


class UserBase(BaseModel):
    """Schema base para usuario."""

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """Schema para crear un nuevo usuario (registro)."""

    password: str = Field(..., min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Valida que la contraseña sea segura:
        - Mínimo 8 caracteres
        - Máximo 72 bytes (límite de bcrypt)
        - Al menos una mayúscula
        - Al menos una minúscula
        - Al menos un número
        - Al menos un símbolo especial
        """
        # Validar longitud en bytes (bcrypt tiene límite de 72 bytes)
        if len(v.encode("utf-8")) > 72:
            raise ValueError("La contraseña no puede exceder 72 bytes")

        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")

        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula")

        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe contener al menos una letra minúscula")

        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>+=\-_\[\]~`;/\\]', v):
            raise ValueError(
                "La contraseña debe contener al menos un símbolo especial."
            )

        return v


class UserLogin(BaseModel):
    """Schema para inicio de sesión."""

    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema para actualización de perfil de usuario."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    """Schema para respuesta de datos de usuario (sin password)."""

    user_id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema para respuesta de autenticación con token JWT."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ForgotPasswordRequest(BaseModel):
    """Schema para solicitud de restablecimiento de contraseña."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Schema para resetear contraseña con token."""

    new_password: str = Field(..., min_length=8, max_length=72)
    confirm_password: str = Field(..., min_length=8, max_length=72)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Valida que la nueva contraseña sea segura."""
        # Validar longitud en bytes (bcrypt tiene límite de 72 bytes)
        if len(v.encode("utf-8")) > 72:
            raise ValueError("La contraseña no puede exceder 72 bytes")

        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")

        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula")

        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe contener al menos una letra minúscula")

        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>+=\-_\[\]~`;/\\]', v):
            raise ValueError(
                "La contraseña debe contener al menos un símbolo especial."
            )

        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """Valida que las contraseñas coincidan."""
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Las contraseñas no coinciden")
        return v
