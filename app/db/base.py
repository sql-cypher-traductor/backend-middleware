from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Importar modelos para Alembic
# Estos imports se hacen después de que Base esté definido
try:
    from app.models.connection import Connection  # noqa: F401, E402
    from app.models.password_reset_token import PasswordResetToken  # noqa: F401, E402
    from app.models.user import User  # noqa: F401, E402
except ImportError:
    # En contexto de tests, los modelos se importarán directamente
    pass
