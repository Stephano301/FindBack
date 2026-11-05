from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Claim, ClaimStatus, Item, ItemKind, ItemStatus, User
from app.schemas.dashboard import DashboardRead
from app.schemas.item import ItemRead

router = APIRouter(prefix="/dashboard", tags=["Tableau de bord"])


@router.get("", response_model=DashboardRead)
def get_dashboard(
    scope: Literal["all", "mine"] = Query(
        "all", description="all = toute l'application, mine = mes annonces seulement"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retourne les statistiques et les 5 dernières annonces."""
    items_query = db.query(Item)
    claims_query = db.query(Claim).filter(Claim.status == ClaimStatus.PENDING)

    if scope == "mine":
        items_query = items_query.filter(Item.owner_id == current_user.id)
        # Demandes en attente reçues sur mes annonces
        claims_query = claims_query.join(Claim.item).filter(
            Item.owner_id == current_user.id
        )

    total_lost = items_query.filter(Item.kind == ItemKind.LOST).count()
    total_found = items_query.filter(Item.kind == ItemKind.FOUND).count()
    total_recovered = items_query.filter(Item.status == ItemStatus.RECOVERED).count()
    pending_claims = claims_query.count()

    latest = (
        items_query.options(joinedload(Item.owner), joinedload(Item.category))
        .order_by(Item.created_at.desc(), Item.id.desc())
        .limit(5)
        .all()
    )

    return DashboardRead(
        total_lost=total_lost,
        total_found=total_found,
        total_recovered=total_recovered,
        pending_claims=pending_claims,
        latest_items=[ItemRead.model_validate(item) for item in latest],
    )