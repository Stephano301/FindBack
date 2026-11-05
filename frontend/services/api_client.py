import requests

import config
from services.session import session


class ApiError(Exception):
    """Erreur renvoyée par l'API ou problème de communication."""

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _error_message(response):
    """Extrait un message lisible de la réponse d'erreur de l'API."""
    try:
        detail = response.json().get("detail")
    except (ValueError, AttributeError):
        detail = None

    if isinstance(detail, str):
        return detail
    if isinstance(detail, list) and detail:
        # Erreur de validation (422) : on garde le premier message
        message = str(detail[0].get("msg", "Données invalides."))
        return "Données invalides : " + message.replace("Value error, ", "")
    return f"Erreur du serveur ({response.status_code})."


def request(method, path, json=None, data=None, files=None, params=None, auth=True):
    """Envoie une requête à l'API et retourne la réponse décodée (ou lève ApiError)."""
    headers = {}
    if auth and session.token:
        headers["Authorization"] = f"Bearer {session.token}"

    try:
        response = requests.request(
            method,
            config.API_BASE_URL + path,
            json=json,
            data=data,
            files=files,
            params=params,
            headers=headers,
            timeout=config.REQUEST_TIMEOUT,
        )
    except requests.exceptions.ConnectionError:
        raise ApiError(
            "Impossible de joindre le serveur. Vérifiez que le backend est lancé."
        )
    except requests.exceptions.Timeout:
        raise ApiError("Le serveur met trop de temps à répondre.")
    except requests.exceptions.RequestException:
        raise ApiError("Erreur de communication avec le serveur.")

    # Jeton refusé : la session est terminée
    if response.status_code == 401 and auth and session.token:
        session.clear()
        raise ApiError("Votre session a expiré. Veuillez vous reconnecter.", 401)

    if not response.ok:
        raise ApiError(_error_message(response), response.status_code)

    if response.status_code == 204 or not response.content:
        return None
    return response.json()