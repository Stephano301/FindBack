from services import api_client, item_service


def stats():
    return api_client.request("GET", "/admin/stats")


def users(query=None, skip=0, limit=200):
    params = {"skip": skip, "limit": limit}
    if query:
        params["q"] = query
    return api_client.request("GET", "/admin/users", params=params)


def claims(status=None, skip=0, limit=200):
    params = {"skip": skip, "limit": limit}
    if status:
        params["status"] = status
    result = api_client.request("GET", "/admin/claims", params=params)
    for claim in result:
        item_service.prepare_item(claim["item"])
    return result


def delete_claim(claim_id):
    api_client.request("DELETE", f"/admin/claims/{claim_id}")