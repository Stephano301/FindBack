import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class ClaimStatus(str, enum.Enum):
    """État d'une demande : en attente, acceptée ou refusée."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Claim(Base):
    __tablename__ = "claims"
    # Un utilisateur ne peut faire qu'une seule demande par annonce
    __table_args__ = (
        UniqueConstraint("item_id", "claimant_id", name="uq_claim_item_claimant"),
    )

    id = Column(Integer, primary_key=True, index=True)
    # Description permettant de prouver que l'objet lui appartient
    message = Column(Text, nullable=False)
    status = Column(
        Enum(ClaimStatus), nullable=False, default=ClaimStatus.PENDING, index=True
    )
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    item_id = Column(
        Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False
    )
    claimant_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    item = relationship("Item", back_populates="claims")
    claimant = relationship("User", back_populates="claims")