import http
import json
from enum import StrEnum, auto, Enum

import requests
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        url = 'http://localhost:8002/api/v1/account/login'
        payload = {'email': username, 'password': password}
        response = requests.post(url, data=json.dumps(payload))

        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()
        # breakpoint()
        try:
            user, created = User.objects.get_or_create(id=data['id'], )
            user.email = data.get('email')
            user.first_name = data.get('firstName')
            user.last_name = data.get('lastName')
            user.is_admin = 'ADMIN' in [role.get('name') for role in data.get('roles')]
            user.is_active = True
            user.save()
        except Exception as e:
            raise e

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None