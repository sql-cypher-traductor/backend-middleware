from sqlalchemy import text

from app.db.session import SessionLocal

try:
    db = SessionLocal()
    db.execute(text("SELECT 1"))
    print("✅ ¡ÉXITO! Python está conectado a la Base de Datos.")
except Exception as e:
    print(f"❌ ERROR: {e}")
