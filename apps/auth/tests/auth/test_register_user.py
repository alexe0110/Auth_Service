from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from tests.utils import check_jwt_tokens


@pytest.mark.usefixtures("add_user")
class TestRegisterAccount:
    @pytest.mark.parametrize(("email", "password"), [("test_email@yandex.ru", "qwerty")])
    def test_register_account(self, client: TestClient, email, password):
        result = client.post(
            "/auth/api/v1/account/register",
            json={
                "email": "mymail@yandex.ru",
                "password": "qwerty",
                "lastName": "White",
                "firstName": "Alex",
                "middleName": "Kek",
                "birthdate": "2000-01-01",
                "gender": "male",
            },
        )
        result_dict = result.json()
        account_id = result_dict.get("id")

        assert result.status_code == HTTPStatus.OK
        assert result_dict.get("email") == "mymail@yandex.ru"
        assert len(result_dict.get("roles")) == 1

        check_jwt_tokens(result.cookies, account_id)

    @pytest.mark.parametrize("email", ["test_email@yandex.ru"])
    def test_register_already_exist_email(self, client: TestClient, email):
        result = client.post(
            "/auth/api/v1/account/register",
            json={
                "email": email,
                "password": "qwerty",
                "lastName": "Asimov",
                "firstName": "Isaac",
                "birthdate": "1920-01-01",
                "gender": "male",
            },
        )
        result_dict = result.json()

        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert result_dict.get("detail") == "User already registered"


class TestChangeCredentials:
    @pytest.mark.parametrize(("email", "password"), [("test_change_credentials_email@yandex.ru", "qwerty")])
    def test_change_credentials_email(self, client: TestClient, add_user, email, password):
        created_user_account_id = add_user
        new_email = "new_email@ya.ru"

        client.post(
            "/auth/api/v1/account/login",
            json={
                "email": email,
                "password": password,
            },
        )

        result = client.patch("/auth/api/v1/account/credentials", json={"email": new_email})
        result_dict = result.json()

        assert result.status_code == HTTPStatus.OK
        assert result_dict.get("email") == new_email

        auth_result = client.post(
            "/auth/api/v1/account/login",
            json={
                "email": new_email,
                "password": password,
            },
        )
        auth_result_dict = auth_result.json()

        assert auth_result.status_code == HTTPStatus.OK
        assert auth_result_dict.get("email") == new_email

        check_jwt_tokens(auth_result.cookies, created_user_account_id)

    @pytest.mark.parametrize(("email", "password"), [("test_change_credentials_password@yandex.ru", "qwerty")])
    def test_change_credentials_password(self, client: TestClient, add_user, email, password):
        created_user_account_id = add_user
        new_password = "new_password"

        client.post(
            "/auth/api/v1/account/login",
            json={
                "email": email,
                "password": password,
            },
        )

        result = client.patch("/auth/api/v1/account/credentials", json={"password": new_password})
        assert result.status_code == HTTPStatus.OK

        auth_result = client.post(
            "/auth/api/v1/account/login",
            json={
                "email": email,
                "password": new_password,
            },
        )
        assert auth_result.status_code == HTTPStatus.OK
        check_jwt_tokens(auth_result.cookies, created_user_account_id)
