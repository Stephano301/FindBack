from datetime import date, datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

from app.models.item import ItemKind, ItemStatus
from app.schemas.category import CategoryRead

Title = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)
]
Description = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=3, max_length=2000)
]
Location = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=2, max_length=150)
]


def check_not_in_future(value: date) -> date:
    """Un objet ne peut pas avoir été perdu ou trouvé dans le futur."""
    if value > date.today():
        raise ValueError("La date ne peut pas être dans le futur.")
    return value


class ItemCreate(BaseModel):
    """Données pour déclarer un objet perdu ou trouvé."""

    kind: ItemKind
    title: Title
    description: Description
    location: Location
    event_date: date
    category_id: int

    @field_validator("event_date")
    @classmethod
    def validate_date(cls, value: date) -> date:
        return check_not_in_future(value)


class ItemUpdate(BaseModel):
    """Données de modification d'une annonce : tous les champs sont facultatifs."""

    title: Optional[Title] = None
    description: Optional[Description] = None
    location: Optional[Location] = None
    event_date: Optional[date] = None
    category_id: Optional[int] = None

    @field_validator("event_date")
    @classmethod
    def validate_date(cls, value: Optional[date]) -> Optional[date]:
        return check_not_in_future(value) if value else value


class ItemStatusUpdate(BaseModel):
    """Changement du statut de récupération."""

    status: ItemStatus


class OwnerRead(BaseModel):
    """Ce que l'on montre publiquement du propriétaire d'une annonce."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    occupation: str
    avatar_path: Optional[str] = None


class ItemRead(BaseModel):
    """Annonce renvoyée par l'API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: ItemKind
    title: str
    description: str
    location: str
    event_date: date
    photo_path: Optional[str] = None
    status: ItemStatus
    created_at: datetime
    owner: OwnerRead
    category: CategoryRead