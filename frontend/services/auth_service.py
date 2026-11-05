from services import api_client


def login(email, password):
    """Connecte l'utilisateur. Retourne (jeton, utilisateur)."""
    # La route de connexion attend un formulaire dont le champ "username" contient l'e-mail
    data = api_client.request(
        "POST",
        "/auth/login",
        data={"username": email, "password": password},
        auth=False,
    )
    return data["access_token"], data["user"]


def register(first_name, last_name, email, password, occupation):
    """Crée le compte puis connecte l'utilisateur. Retourne (jeton, utilisateur)."""
    api_client.request(
        "POST",
        "/auth/register",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
            "occupation": occupation,
        },
        auth=False,
    )
    return login(email, password)