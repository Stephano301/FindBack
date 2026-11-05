# Adresse du backend FastAPI (lancé avec uvicorn dans le dossier backend)
API_BASE_URL = "http://127.0.0.1:8000"

# Temps d'attente maximum d'une réponse, en secondes
REQUEST_TIMEOUT = 8


def media_url(path):
    """Transforme 'items/abc.jpg' en adresse complète de l'image (ou None s'il n'y en a pas)."""
    if not path:
        return None
    return f"{API_BASE_URL}/uploads/{path}"