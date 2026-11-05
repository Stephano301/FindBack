from pydantic import BaseModel

from app.schemas.item import ItemRead


class DashboardRead(BaseModel):
    """Chiffres et dernières annonces affichés sur l'écran d'accueil."""

    total_lost: int
    total_found: int
    total_recovered: int
    pending_claims: int
    latest_items: list[ItemRead]


class AdminStats(BaseModel):
    """Statistiques globales pour l'administrateur."""

    total_users: int
    total_items: int
    total_lost: int
    total_found: int
    total_recovered: int
    claims_pending: int
    claims_accepted: int
    claims_rejected: int