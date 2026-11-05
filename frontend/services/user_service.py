import os

import config
from services import api_client


def get_me():
    return api_client.request("GET", "/users/me")


def update_me(changes):
    return api_client.request("PUT", "/users/me", json=changes)


def change_password(current_password, new_password):
    return api_client.request(
        "PUT",
        "/users/me/password",
        json={"current_password": current_password, "new_password": new_password},
    )


def upload_avatar(file_path):
    with open(file_path, "rb") as file:
        return api_client.request(
            "POST",
            "/users/me/avatar",
            files={"file": (os.path.basename(file_path), file)},
        )


def avatar_url(user):
    return config.media_url(user.get("avatar_path"))