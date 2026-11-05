from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Claim, ClaimStatus, Item, ItemStatus, User
from app.schemas.claim import ClaimCreate, ClaimDecision, ClaimRead

router = APIRouter(prefix="/claims", tags=["Demandes de récupération"])


# ---------- Fonctions utilitaires ----------


def base_query(db: Session):
    """Requête de base : charge aussi le demandeur, l'annonce et son propriétaire."""
    return db.query(Claim).options(
        joinedload(Claim.claimant),
        joinedload(Claim.item).joinedload(Item.owner),
    )


def get_claim_or_404(db: Session, claim_id: int) -> Claim:
    claim = base_query(db).filter(Claim.id == claim_id).first()
    if claim is None:
        raise HTTPException(status_code=404, detail="Demande introuvable.")
    return claim


def build_claim_read(claim: Claim, viewer: User) -> ClaimRead:
    """Prépare la réponse. L'e-mail de l'autre personne n'apparaît qu'après acceptation."""
    result = ClaimRead.model_validate(claim)
    if claim.status == ClaimStatus.ACCEPTED:
        if viewer.id == claim.claimant_id:
            result.contact_email = claim.item.owner.email
        elif viewer.id == claim.item.owner_id:
            result.contact_email = claim.claimant.email
    return result


# ---------- Routes ----------


@router.post("", response_model=ClaimRead, status_code=201)
def create_claim(
    data: ClaimCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Envoie une demande pour réclamer un objet."""
    item = db.get(Item, data.item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Annonce introuvable.")
    if item.owner_id == current_user.id:
        raise HTTPException(
            status_code=400, detail="Vous ne pouvez pas réclamer votre propre annonce."
        )
    if item.status == ItemStatus.RECOVERED:
        raise HTTPException(status_code=400, detail="Cet objet a déjà été récupéré.")

    already_sent = (
        db.query(Claim)
        .filter(Claim.item_id == item.id, Claim.claimant_id == current_user.id)
        .first()
    )
    if already_sent:
        raise HTTPException(
            status_code=409, detail="Vous avez déjà envoyé une demande pour cet objet."
        )

    claim = Claim(item_id=item.id, claimant_id=current_user.id, message=data.message)
    db.add(claim)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Vous avez déjà envoyé une demande pour cet objet."
        )

    return build_claim_read(get_claim_or_404(db, claim.id), current_user)


# IMPORTANT : "/received" et "/sent" doivent rester AVANT "/{claim_id}"
@router.get("/received", response_model=list[ClaimRead])
def list_received_claims(
    status: Optional[ClaimStatus] = Query(None, description="pending, accepted ou rejected"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Liste les demandes reçues sur mes annonces."""
    query = base_query(db).join(Claim.item).filter(Item.owner_id == current_user.id)
    if status:
        query = query.filter(Claim.status == status)
    claims = query.order_by(Claim.created_at.desc(), Claim.id.desc()).all()
    return [build_claim_read(claim, current_user) for claim in claims]


@router.get("/sent", response_model=list[ClaimRead])
def list_sent_claims(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Liste les demandes que j'ai envoyées."""
    claims = (
        base_query(db)
        .filter(Claim.claimant_id == current_user.id)
        .order_by(Claim.created_at.desc(), Claim.id.desc())
        .all()
    )
    return [build_claim_read(claim, current_user) for claim in claims]


@router.get("/{claim_id}", response_model=ClaimRead)
def read_claim(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Détail d'une demande (visible par le demandeur, le propriétaire ou un administrateur)."""
    claim = get_claim_or_404(db, claim_id)
    allowed = (
        current_user.id == claim.claimant_id
        or current_user.id == claim.item.owner_id
        or current_user.is_admin
    )
    if not allowed:
        raise HTTPException(status_code=403, detail="Accès refusé à cette demande.")
    return build_claim_read(claim, current_user)


@router.put("/{claim_id}/decision", response_model=ClaimRead)
def decide_claim(
    claim_id: int,
    data: ClaimDecision,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Accepte ou refuse une demande (propriétaire de l'annonce uniquement)."""
    claim = get_claim_or_404(db, claim_id)
    if claim.item.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Seul le propriétaire de l'annonce peut répondre à cette demande.",
        )
    if claim.status != ClaimStatus.PENDING:
        raise HTTPException(
            status_code=400, detail="Cette demande a déjà reçu une réponse."
        )

    claim.status = data.status
    if data.status == ClaimStatus.ACCEPTED:
        # L'objet est récupéré, et les autres demandes en attente sont refusées
        claim.item.status = ItemStatus.RECOVERED
        (
            db.query(Claim)
            .filter(
                Claim.item_id == claim.item_id,
                Claim.id != claim.id,
                Claim.status == ClaimStatus.PENDING,
            )
            .update({Claim.status: ClaimStatus.REJECTED}, synchronize_session=False)
        )

    db.commit()
    return build_claim_read(get_claim_or_404(db, claim_id), current_user)


@router.delete("/{claim_id}", status_code=204)
def cancel_claim(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Annule sa propre demande, tant qu'elle est en attente."""
    claim = get_claim_or_404(db, claim_id)
    if claim.claimant_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Vous ne pouvez annuler que vos propres demandes."
        )
    if claim.status != ClaimStatus.PENDING:
        raise HTTPException(
            status_code=400, detail="Seule une demande en attente peut être annulée."
        )

    db.delete(claim)
    db.commit()
    return Response(status_code=204)