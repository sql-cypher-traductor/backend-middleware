from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Importar modelos para que SQLAlchemy los registre en Base.metadata
# Estos imports deben hacerse después de que Base esté definido
from app.models.connection import Connection  # noqa: F401, E402
from app.models.password_reset_token import PasswordResetToken  # noqa: F401, E402
from app.models.user import User  # noqa: F401, E402
