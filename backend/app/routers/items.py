from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.files import delete_image, save_image
from app.models import Category, Item, ItemKind, ItemStatus, User
from app.schemas.item import ItemCreate, ItemRead, ItemStatusUpdate, ItemUpdate

router = APIRouter(prefix="/items", tags=["Objets perdus et trouvés"])


# ---------- Fonctions utilitaires ----------


def base_query(db: Session):
    """Requête de base : charge aussi le propriétaire et la catégorie."""
    return db.query(Item).options(joinedload(Item.owner), joinedload(Item.category))


def get_item_or_404(db: Session, item_id: int) -> Item:
    item = base_query(db).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Annonce introuvable.")
    return item


def ensure_owner(item: Item, user: User) -> None:
    if item.owner_id != user.id:
        raise HTTPException(
            status_code=403, detail="Vous ne pouvez modifier que vos propres annonces."
        )


def ensure_category_exists(db: Session, category_id: int) -> None:
    if db.get(Category, category_id) is None:
        raise HTTPException(status_code=400, detail="Catégorie introuvable.")


# ---------- Routes ----------


@router.post("", response_model=ItemRead, status_code=201)
def create_item(
    data: ItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Déclare un objet perdu ou trouvé."""
    ensure_category_exists(db, data.category_id)
    item = Item(**data.model_dump(), owner_id=current_user.id)
    db.add(item)
    db.commit()
    return get_item_or_404(db, item.id)


@router.get("", response_model=list[ItemRead])
def list_items(
    kind: Optional[ItemKind] = Query(None, description="lost = perdu, found = trouvé"),
    q: Optional[str] = Query(None, description="Recherche par nom de l'objet"),
    category_id: Optional[int] = Query(None, description="Filtre par catégorie"),
    location: Optional[str] = Query(None, description="Filtre par lieu"),
    status: Optional[ItemStatus] = Query(None, description="pending ou recovered"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Liste les annonces (les plus récentes d'abord), avec recherche et filtres."""
    query = base_query(db)
    if kind:
        query = query.filter(Item.kind == kind)
    if q and q.strip():
        query = query.filter(Item.title.ilike(f"%{q.strip()}%"))
    if category_id:
        query = query.filter(Item.category_id == category_id)
    if location and location.strip():
        query = query.filter(Item.location.ilike(f"%{location.strip()}%"))
    if status:
        query = query.filter(Item.status == status)

    return (
        query.order_by(Item.created_at.desc(), Item.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# IMPORTANT : cette route doit rester AVANT "/{item_id}"
@router.get("/mine", response_model=list[ItemRead])
def list_my_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Liste les annonces de l'utilisateur connecté."""
    return (
        base_query(db)
        .filter(Item.owner_id == current_user.id)
        .order_by(Item.created_at.desc(), Item.id.desc())
        .all()
    )


@router.get("/{item_id}", response_model=ItemRead)
def read_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retourne le détail d'une annonce."""
    return get_item_or_404(db, item_id)


@router.put("/{item_id}", response_model=ItemRead)
def update_item(
    item_id: int,
    data: ItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Modifie une annonce (propriétaire uniquement). Seuls les champs envoyés changent."""
    item = get_item_or_404(db, item_id)
    ensure_owner(item, current_user)

    changes = data.model_dump(exclude_unset=True)
    if changes.get("category_id") is not None:
        ensure_category_exists(db, changes["category_id"])

    for field, value in changes.items():
        if value is not None:
            setattr(item, field, value)

    db.commit()
    return get_item_or_404(db, item_id)


@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Supprime une annonce (propriétaire ou administrateur)."""
    item = get_item_or_404(db, item_id)
    if item.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403, detail="Vous ne pouvez supprimer que vos propres annonces."
        )

    photo_path = item.photo_path
    db.delete(item)
    db.commit()
    delete_image(photo_path)
    return Response(status_code=204)


@router.post("/{item_id}/photo", response_model=ItemRead)
def upload_item_photo(
    item_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Ajoute ou remplace la photo d'une annonce (propriétaire uniquement)."""
    item = get_item_or_404(db, item_id)
    ensure_owner(item, current_user)

    new_path = save_image(file, "items")
    delete_image(item.photo_path)
    item.photo_path = new_path
    db.commit()
    return get_item_or_404(db, item_id)


@router.put("/{item_id}/status", response_model=ItemRead)
def update_item_status(
    item_id: int,
    data: ItemStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change le statut de récupération (propriétaire uniquement)."""
    item = get_item_or_404(db, item_id)
    ensure_owner(item, current_user)

    item.status = data.status
    db.commit()
    return get_item_or_404(db, item_id)