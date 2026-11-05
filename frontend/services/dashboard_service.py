from services import api_client, item_service


def get_dashboard(scope="all"):
    """scope : 'all' (toute l'application) ou 'mine' (mes annonces seulement)."""
    data = api_client.request("GET", "/dashboard", params={"scope": scope})
    data["latest_items"] = [
        item_service.prepare_item(item) for item in data["latest_items"]
    ]
    return data