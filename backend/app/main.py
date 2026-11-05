from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import models  # noqa: F401  (fait connaître les modèles à SQLAlchemy)
from app.config import APP_NAME, UPLOAD_DIR
from app.database import Base, SessionLocal, engine, get_db
from app.routers import admin, auth, categories, claims, dashboard, items, users
from app.seed import create_default_categories

# Crée le dossier des photos s'il n'existe pas encore
UPLOAD_DIR.mkdir(exist_ok=True)

# Crée dans findback.db les tables qui n'existent pas encore
Base.metadata.create_all(bind=engine)

# Ajoute les catégories par défaut si besoin
with SessionLocal() as db:
    create_default_categories(db)

# L'application FastAPI. Le titre et la description apparaissent dans Swagger.
app = FastAPI(
    title=APP_NAME,
    description="API de gestion des objets perdus et trouvés.",
    version="1.0.0",
)

# Rend les images accessibles à l'adresse /uploads/...
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Branchement des groupes de routes
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(items.router)
app.include_router(claims.router)
app.include_router(dashboard.router)
app.include_router(admin.router)


@app.get("/")
def accueil():
    """Route de bienvenue : permet de vérifier que l'API est en ligne."""
    return {"message": "Bienvenue sur l'API FindBack", "statut": "en ligne"}


@app.get("/sante")
def verifier_sante(db: Session = Depends(get_db)):
    """Vérifie que l'API peut bien parler à la base de données."""
    db.execute(text("SELECT 1"))
    return {"api": "ok", "base_de_donnees": "ok"}