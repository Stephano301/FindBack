from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    # On ne stocke JAMAIS le mot de passe : seulement son hachage
    password_hash = Column(String(255), nullable=False)
    occupation = Column(String(50), nullable=False, default="Étudiant")
    avatar_path = Column(String(255), nullable=True)
    is_admin = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relations : les annonces et les demandes de cet utilisateur.
    # Si l'utilisateur est supprimé, ses annonces et demandes le sont aussi.
    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")
    claims = relationship(
        "Claim", back_populates="claimant", cascade="all, delete-orphan"
    )