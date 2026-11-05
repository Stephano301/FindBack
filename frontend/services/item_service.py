import os

import config
from services import api_client


def prepare_item(item):
    """Ajoute l'adresse complète de la photo, utilisée par l'interface."""
    item["photo_url"] = config.media_url(item.get("photo_path"))
    return item


def list_items(
    kind=None,
    query=None,
    category_id=None,
    location=None,
    status=None,
    skip=0,
    limit=100,
):
    params = {"skip": skip, "limit": limit}
    if kind:
        params["kind"] = kind
    if query:
        params["q"] = query
    if category_id:
        params["category_id"] = category_id
    if location:
        params["location"] = location
    if status:
        params["status"] = status
    items = api_client.request("GET", "/items", params=params)
    return [prepare_item(item) for item in items]


def my_items():
    items = api_client.request("GET", "/items/mine")
    return [prepare_item(item) for item in items]


def get_item(item_id):
    return prepare_item(api_client.request("GET", f"/items/{item_id}"))


def create_item(payload):
    return prepare_item(api_client.request("POST", "/items", json=payload))


def update_item(item_id, changes):
    return prepare_item(api_client.request("PUT", f"/items/{item_id}", json=changes))


def delete_item(item_id):
    api_client.request("DELETE", f"/items/{item_id}")


def upload_photo(item_id, file_path):
    """Envoie la photo d'une annonce (JPG, PNG ou WEBP, 5 Mo maximum)."""
    with open(file_path, "rb") as file:
        item = api_client.request(
            "POST",
            f"/items/{item_id}/photo",
            files={"file": (os.path.basename(file_path), file)},
        )
    return prepare_item(item)


def set_status(item_id, status):
    """status : 'pending' ou 'recovered'."""
    return prepare_item(
        api_client.request("PUT", f"/items/{item_id}/status", json={"status": status})
    )