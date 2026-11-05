import uuid

from fastapi import HTTPException, UploadFile

from app.config import UPLOAD_DIR

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 Mo


def _detect_extension(content: bytes) -> str | None:
    """Reconnaît le vrai format de l'image grâce à ses premiers octets."""
    if content.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return ".webp"
    return None


def save_image(upload: UploadFile, subfolder: str) -> str:
    """Vérifie puis enregistre une image. Retourne son chemin relatif, ex : avatars/abc123.jpg"""
    content = upload.file.read(MAX_IMAGE_SIZE + 1)
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, detail="Image trop lourde (5 Mo maximum).")

    extension = _detect_extension(content)
    if extension is None:
        raise HTTPException(
            status_code=400,
            detail="Format d'image non accepté. Utilisez JPG, PNG ou WEBP.",
        )

    folder = UPLOAD_DIR / subfolder
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{extension}"
    (folder / filename).write_bytes(content)
    return f"{subfolder}/{filename}"


def delete_image(relative_path: str | None) -> None:
    """Supprime une image enregistrée (sans effet si elle n'existe plus)."""
    if not relative_path:
        return
    path = (UPLOAD_DIR / relative_path).resolve()
    # Sécurité : on ne supprime que des fichiers situés dans le dossier uploads
    if UPLOAD_DIR.resolve() in path.parents and path.is_file():
        path.unlink(missing_ok=True)