from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category
from app.schemas.category import CategoryRead

router = APIRouter(prefix="/categories", tags=["Catégories"])


@router.get("", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    """Retourne toutes les catégories, triées par nom."""
    return db.query(Category).order_by(Category.name).all()