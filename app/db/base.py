from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# NOTA: No importar modelos aquí para evitar importaciones circulares.
# Los modelos se importan en app/db/session.py o donde se necesite
# inicializar la metadata de SQLAlchemy.
