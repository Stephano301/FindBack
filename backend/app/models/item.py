import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class ItemKind(str, enum.Enum):
    """Type d'annonce : objet perdu ou objet trouvé."""

    LOST = "lost"
    FOUND = "found"


class ItemStatus(str, enum.Enum):
    """État de l'annonce : en attente de récupération, ou récupéré."""

    PENDING = "pending"
    RECOVERED = "recovered"


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    kind = Column(Enum(ItemKind), nullable=False, index=True)
    title = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    location = Column(String(150), nullable=False, index=True)
    # Date de la perte ou de la découverte
    event_date = Column(Date, nullable=False)
    photo_path = Column(String(255), nullable=True)
    status = Column(
        Enum(ItemStatus), nullable=False, default=ItemStatus.PENDING, index=True
    )
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Clés étrangères : le lien vers l'utilisateur et la catégorie
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    owner = relationship("User", back_populates="items")
    category = relationship("Category", back_populates="items")
    claims = relationship(
        "Claim", back_populates="item", cascade="all, delete-orphan"
    )