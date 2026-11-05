from services import api_client, item_service


def _prepare(claim):
    item_service.prepare_item(claim["item"])
    return claim


def create_claim(item_id, message):
    claim = api_client.request(
        "POST", "/claims", json={"item_id": item_id, "message": message}
    )
    return _prepare(claim)


def received(status=None):
    params = {"status": status} if status else None
    claims = api_client.request("GET", "/claims/received", params=params)
    return [_prepare(claim) for claim in claims]


def sent():
    claims = api_client.request("GET", "/claims/sent")
    return [_prepare(claim) for claim in claims]


def decide(claim_id, status):
    """status : 'accepted' ou 'rejected'."""
    claim = api_client.request(
        "PUT", f"/claims/{claim_id}/decision", json={"status": status}
    )
    return _prepare(claim)


def cancel(claim_id):
    api_client.request("DELETE", f"/claims/{claim_id}")