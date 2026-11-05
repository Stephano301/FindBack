from sqlalchemy.orm import Session

from app.models import Category

DEFAULT_CATEGORIES = [
    "Clés",
    "Téléphone",
    "Sac",
    "Portefeuille",
    "Documents",
    "Vêtements",
    "Électronique",
    "Bijoux",
    "Autre",
]


def create_default_categories(db: Session) -> None:
    """Ajoute les catégories par défaut, seulement si aucune n'existe encore."""
    if db.query(Category).count() == 0:
        db.add_all([Category(name=name) for name in DEFAULT_CATEGORIES])
        db.commit()