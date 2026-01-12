"""Servicio para gestión de autenticación y autorización."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate


class AuthService:
    """Servicio para gestión de autenticación y autorización."""

    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """Registra un nuevo usuario en el sistema.

        Args:
            db: Sesión de base de datos
            user_data: Datos del usuario a registrar

        Returns:
            Usuario creado

        Raises:
            ValueError: Si el email ya está registrado
        """
        # Validar que el email sea único
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("El email ya está registrado")

        # Crear nuevo usuario con contraseña encriptada
        new_user = User(
            name=user_data.name,
            last_name=user_data.last_name,
            email=user_data.email,
            password=get_password_hash(user_data.password),
            role=UserRole.DEV,  # Asignar rol DEV por defecto
            is_active=True,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Autentica un usuario con email y contraseña.

        Args:
            db: Sesión de base de datos
            email: Email del usuario
            password: Contraseña en texto plano

        Returns:
            Usuario autenticado o None si las credenciales son inválidas
        """
        user = db.query(User).filter(User.email == email).first()

        if not user:
            return None

        if not verify_password(password, user.password):
            return None

        if not user.is_active:
            return None

        # Actualizar última sesión
        user.last_login = datetime.now(timezone.utc)
        db.commit()

        return user

    @staticmethod
    def create_access_token_for_user(user: User) -> str:
        """Crea un token JWT para un usuario.

        Args:
            user: Usuario para el cual se genera el token

        Returns:
            Token JWT codificado
        """
        token_data = {
            "sub": str(user.user_id),
            "email": user.email,
            "role": user.role.value,
        }

        return create_access_token(token_data)

    @staticmethod
    def update_user_profile(
        db: Session,
        user: User,
        name: Optional[str],
        last_name: Optional[str],
        email: Optional[str],
    ) -> User:
        """Actualiza el perfil de un usuario.

        Args:
            db: Sesión de base de datos
            user: Usuario a actualizar
            name: Nuevo nombre (opcional)
            last_name: Nuevo apellido (opcional)
            email: Nuevo email (opcional)

        Returns:
            Usuario actualizado

        Raises:
            ValueError: Si el nuevo email ya está en uso por otro usuario
        """
        if name is not None:
            user.name = name

        if last_name is not None:
            user.last_name = last_name

        if email is not None and email != user.email:
            # Validar que el nuevo email no esté en uso
            existing_user = (
                db.query(User)
                .filter(User.email == email, User.user_id != user.user_id)
                .first()
            )
            if existing_user:
                raise ValueError("El email ya está en uso")
            user.email = email

        db.commit()
        db.refresh(user)

        return user
