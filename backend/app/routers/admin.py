from typing import Optional

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin
from app.models import Claim, ClaimStatus, Item, ItemKind, ItemStatus, User
from app.routers.claims import base_query as claims_base_query
from app.routers.claims import build_claim_read, get_claim_or_404
from app.schemas.claim import ClaimRead
from app.schemas.dashboard import AdminStats
from app.schemas.user import UserRead

# Toutes les routes de ce fichier exigent un administrateur
router = APIRouter(
    prefix="/admin",
    tags=["Administration"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("/stats", response_model=AdminStats)
def admin_stats(db: Session = Depends(get_db)):
    """Statistiques globales de l'application."""
    return AdminStats(
        total_users=db.query(User).count(),
        total_items=db.query(Item).count(),
        total_lost=db.query(Item).filter(Item.kind == ItemKind.LOST).count(),
        total_found=db.query(Item).filter(Item.kind == ItemKind.FOUND).count(),
        total_recovered=db.query(Item)
        .filter(Item.status == ItemStatus.RECOVERED)
        .count(),
        claims_pending=db.query(Claim)
        .filter(Claim.status == ClaimStatus.PENDING)
        .count(),
        claims_accepted=db.query(Claim)
        .filter(Claim.status == ClaimStatus.ACCEPTED)
        .count(),
        claims_rejected=db.query(Claim)
        .filter(Claim.status == ClaimStatus.REJECTED)
        .count(),
    )


@router.get("/users", response_model=list[UserRead])
def list_users(
    q: Optional[str] = Query(None, description="Recherche par nom ou e-mail"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Liste les utilisateurs inscrits (les plus récents d'abord)."""
    query = db.query(User)
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        query = query.filter(
            or_(
                User.first_name.ilike(pattern),
                User.last_name.ilike(pattern),
                User.email.ilike(pattern),
            )
        )
    return (
        query.order_by(User.created_at.desc(), User.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/claims", response_model=list[ClaimRead])
def list_all_claims(
    status: Optional[ClaimStatus] = Query(None, description="pending, accepted ou rejected"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Liste toutes les demandes de récupération de l'application."""
    query = claims_base_query(db)
    if status:
        query = query.filter(Claim.status == status)
    claims = (
        query.order_by(Claim.created_at.desc(), Claim.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [build_claim_read(claim, admin) for claim in claims]


@router.delete("/claims/{claim_id}", status_code=204)
def delete_claim(claim_id: int, db: Session = Depends(get_db)):
    """Supprime une demande (par exemple une demande abusive)."""
    claim = get_claim_or_404(db, claim_id)
    db.delete(claim)
    db.commit()
    return Response(status_code=204)