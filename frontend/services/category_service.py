from services import api_client


def list_categories():
    return api_client.request("GET", "/categories")