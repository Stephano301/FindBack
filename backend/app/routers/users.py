from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.files import delete_image, save_image
from app.models import User
from app.schemas.user import PasswordChange, UserRead, UserUpdate
from app.security import hash_password, verify_password

router = APIRouter(prefix="/users", tags=["Utilisateurs"])


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Retourne le profil de l'utilisateur connecté."""
    return current_user


@router.put("/me", response_model=UserRead)
def update_current_user(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Modifie le profil. Seuls les champs envoyés sont modifiés."""
    changes = data.model_dump(exclude_unset=True)

    new_email = changes.get("email")
    if new_email and new_email != current_user.email:
        already_used = db.query(User).filter(User.email == new_email).first()
        if already_used:
            raise HTTPException(
                status_code=409, detail="Cet e-mail est déjà utilisé par un autre compte."
            )

    for field, value in changes.items():
        if value is not None:
            setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/me/password")
def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change le mot de passe, après vérification de l'ancien."""
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect.")

    current_user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"message": "Mot de passe modifié avec succès."}


@router.post("/me/avatar", response_model=UserRead)
def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Enregistre la photo de profil et remplace l'ancienne."""
    new_path = save_image(file, "avatars")
    delete_image(current_user.avatar_path)

    current_user.avatar_path = new_path
    db.commit()
    db.refresh(current_user)
    return current_user