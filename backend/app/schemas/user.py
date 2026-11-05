from datetime import datetime
from typing import Annotated, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    field_validator,
)

# Texte court : espaces au début et à la fin retirés, entre 2 et 50 caractères
ShortText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=2, max_length=50)
]


def validate_password_strength(value: str) -> str:
    """Règles communes à tous les nouveaux mots de passe."""
    # bcrypt ne gère que 72 octets au maximum
    if len(value.encode("utf-8")) > 72:
        raise ValueError("Le mot de passe est trop long.")
    if not any(c.isalpha() for c in value) or not any(c.isdigit() for c in value):
        raise ValueError(
            "Le mot de passe doit contenir au moins une lettre et un chiffre."
        )
    return value


class UserCreate(BaseModel):
    """Données demandées pour créer un compte."""

    first_name: ShortText
    last_name: ShortText
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    occupation: ShortText = "Étudiant"

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: str) -> str:
        # On enregistre toujours l'e-mail en minuscules
        return value.lower()

    @field_validator("password")
    @classmethod
    def check_password(cls, value: str) -> str:
        return validate_password_strength(value)


class UserUpdate(BaseModel):
    """Données de modification du profil : tous les champs sont facultatifs."""

    first_name: Optional[ShortText] = None
    last_name: Optional[ShortText] = None
    email: Optional[EmailStr] = None
    occupation: Optional[ShortText] = None

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: Optional[str]) -> Optional[str]:
        return value.lower() if value else value


class PasswordChange(BaseModel):
    """Données pour changer son mot de passe."""

    current_password: str
    new_password: str = Field(min_length=8, max_length=64)

    @field_validator("new_password")
    @classmethod
    def check_new_password(cls, value: str) -> str:
        return validate_password_strength(value)


class UserRead(BaseModel):
    """Données renvoyées par l'API sur un utilisateur (jamais le mot de passe)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: str
    occupation: str
    avatar_path: Optional[str] = None
    is_admin: bool
    created_at: datetime


class TokenResponse(BaseModel):
    """Réponse à une connexion réussie : le jeton et l'utilisateur."""

    access_token: str
    token_type: str = "bearer"
    user: UserRead