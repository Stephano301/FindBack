from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

from app.models.claim import ClaimStatus
from app.models.item import ItemKind, ItemStatus
from app.schemas.item import OwnerRead

ClaimMessage = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=10, max_length=1000)
]


class ClaimCreate(BaseModel):
    """Données pour réclamer un objet."""

    item_id: int
    # Description permettant de prouver que l'objet appartient bien à la personne
    message: ClaimMessage


class ClaimDecision(BaseModel):
    """Réponse du propriétaire : accepted ou rejected."""

    status: ClaimStatus

    @field_validator("status")
    @classmethod
    def only_final_decision(cls, value: ClaimStatus) -> ClaimStatus:
        if value == ClaimStatus.PENDING:
            raise ValueError("La décision doit être 'accepted' ou 'rejected'.")
        return value


class ItemSummary(BaseModel):
    """Résumé de l'annonce concernée par une demande."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: ItemKind
    title: str
    location: str
    photo_path: Optional[str] = None
    status: ItemStatus
    owner: OwnerRead


class ClaimRead(BaseModel):
    """Demande renvoyée par l'API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    message: str
    status: ClaimStatus
    created_at: datetime
    item: ItemSummary
    claimant: OwnerRead
    # Rempli seulement quand la demande est acceptée (pour organiser la remise)
    contact_email: Optional[str] = None