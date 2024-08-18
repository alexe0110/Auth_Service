import http
import json
import os

import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

User = get_user_model()
auth_api_url = os.environ.get("AUTH_API_URL")


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        url = f"{auth_api_url}/api/v1/account/login"
        payload = {"email": username, "password": password}
        response = requests.post(url, data=json.dumps(payload))

        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()
        try:
            user, created = User.objects.get_or_create(
                id=data["id"],
            )
            user.email = data.get("email")
            user.first_name = data.get("firstName")
            user.last_name = data.get("lastName")
            user.is_admin = "ADMIN" in [role.get("name") for role in data.get("roles")]
            user.is_active = True
            user.save()
        except Exception:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
