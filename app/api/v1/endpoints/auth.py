from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.services.password_reset_service import PasswordResetService

router = APIRouter()


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):  # noqa: B008
    """Registrar un nuevo usuario en el sistema.

    - **email**: Email único del usuario
    - **password**: Contraseña segura (mín 8 chars, mayúsculas, números, símbolos)
    - **name**: Nombre del usuario
    - **last_name**: Apellido del usuario

    Returns:
        Token JWT y datos del usuario creado
    """
    try:
        # Registrar usuario
        new_user = AuthService.register_user(db, user_data)

        # Generar token JWT
        access_token = AuthService.create_access_token_for_user(new_user)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(new_user),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):  # noqa: B008
    """Iniciar sesión en el sistema.

    - **email**: Email del usuario
    - **password**: Contraseña del usuario

    Returns:
        Token JWT y datos del usuario autenticado
    """
    # Autenticar usuario
    user = AuthService.authenticate_user(db, credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generar token JWT
    access_token = AuthService.create_access_token_for_user(user)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):  # noqa: B008
    """Obtener información del usuario autenticado.

    Requiere token JWT válido en el header Authorization: Bearer <token>

    Returns:
        Datos del usuario actual
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    """Actualizar el perfil del usuario autenticado.

    - **name**: Nuevo nombre (opcional)
    - **last_name**: Nuevo apellido (opcional)
    - **email**: Nuevo email (opcional)

    Requiere token JWT válido en el header Authorization: Bearer <token>

    Returns:
        Datos del usuario actualizado
    """
    try:
        updated_user = AuthService.update_user_profile(
            db=db,
            user=current_user,
            name=user_update.name,
            last_name=user_update.last_name,
            email=user_update.email,
        )

        return UserResponse.model_validate(updated_user)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.post("/forgot-password", response_model=dict)
def forgot_password(
    request: ForgotPasswordRequest, db: Session = Depends(get_db)  # noqa: B008
):
    """Solicitar restablecimiento de contraseña mediante email.

    Genera un token único de un solo uso y envía email con enlace
    para restablecer la contraseña. El enlace expira en 30 minutos.

    - **email**: Email de la cuenta

    Returns:
        Mensaje genérico (por seguridad, siempre indica éxito)

    Note:
        Por motivos de seguridad, este endpoint siempre retorna el mismo
        mensaje, independientemente de si el email existe o no en el sistema.
    """
    # Crear token de restablecimiento (retorna None si el email no existe)
    token = PasswordResetService.create_reset_token(db, request.email)

    # Si el token fue creado (email existe), enviar email
    if token:
        EmailService.send_password_reset_email(
            to_email=request.email,
            token=token,
            # En producción, pasar la URL del frontend desde configuración
            reset_url="http://localhost:3000/reset-password",
        )

    # Por seguridad, siempre retornar el mismo mensaje
    # (no revelar si el email existe o no)
    return {
        "message": (
            "Si el email existe en nuestro sistema, "
            "recibirás un enlace para restablecer tu contraseña"
        )
    }


@router.post("/reset-password/{token}", response_model=dict)
def reset_password_with_token(
    token: str,
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),  # noqa: B008
):
    """Restablecer contraseña usando token válido del email.

    - **token**: Token recibido por email (en la URL)
    - **new_password**: Nueva contraseña segura
    - **confirm_password**: Confirmación de la nueva contraseña

    Returns:
        Mensaje de confirmación

    Raises:
        HTTPException 400: Si el token es inválido, expiró o ya fue usado
    """
    # Intentar restablecer contraseña con el token
    success = PasswordResetService.reset_password_with_token(
        db, token, request.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido, expirado o ya usado",
        )

    # Obtener usuario para enviar notificación
    reset_token = PasswordResetService.validate_reset_token(db, token)
    if reset_token:
        user = db.query(User).filter(User.user_id == reset_token.user_id).first()
        if user:
            EmailService.send_password_changed_notification(user.email)

    return {
        "message": (
            "Contraseña restablecida exitosamente. "
            "Por favor, inicia sesión con tu nueva contraseña"
        )
    }
