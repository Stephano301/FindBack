from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

# Le moteur : il connaît l'emplacement du fichier SQLite.
# check_same_thread=False est nécessaire avec FastAPI et SQLite.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


# SQLite n'applique pas les relations entre tables par défaut.
# Cette fonction les active à chaque connexion (clés étrangères).
@event.listens_for(engine, "connect")
def activer_cles_etrangeres(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Fabrique de sessions : chaque requête obtiendra sa propre session.
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Classe de départ de tous nos modèles (les futures tables)
Base = declarative_base()


def get_db():
    """Ouvre une session pour une requête, puis la ferme toujours à la fin."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()