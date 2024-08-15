from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from tests.utils import check_jwt_tokens


@pytest.mark.usefixtures("add_user")
@pytest.mark.parametrize(("email", "password"), [("test_email@yandex.ru", "qwerty")])
class TestLogin:
    def test_login(self, client: TestClient, email, password):
        result = client.post(
            "/auth/api/v1/account/login",
            json={
                "email": email,
                "password": password,
            },
        )
        result_dict = result.json()
        account_id = result_dict.get("id")

        assert result.status_code == HTTPStatus.OK
        assert result_dict.get("email") == "test_email@yandex.ru"

        check_jwt_tokens(result.cookies, account_id)

    def test_login_user_wrong_password(self, client: TestClient, email):
        result = client.post(
            "/auth/api/v1/account/login",
            json={
                "email": email,
                "password": "fake_password",
            },
        )
        result_dict = result.json()

        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert result_dict.get("detail") == "Invalid credentials"

        assert not result.cookies.get("access_token")
        assert not result.cookies.get("refresh_token")


class TestLogout:
    @pytest.mark.usefixtures("add_user")
    @pytest.mark.parametrize(("email", "password"), [("test_email@yandex.ru", "qwerty")])
    def test_logout(self, client: TestClient, email, password):
        auth_result = client.post(
            "/auth/api/v1/account/login",
            json={
                "email": email,
                "password": password,
            },
        )

        result = client.post(
            "/auth/api/v1/account/logout", cookies={"refresh_token": auth_result.cookies.get("refresh_token")}
        )

        assert result.status_code == HTTPStatus.NO_CONTENT
        assert result.text == ""

        assert not result.cookies.get("access_token")
        assert not result.cookies.get("refresh_token")

    def test_logout_unauthorized(self, client: TestClient):
        result = client.post("/auth/api/v1/account/logout")
        result_dict = result.json()

        assert result.status_code == HTTPStatus.UNAUTHORIZED
        assert result_dict.get("detail") == "Authorization required"


class TestRefreshToken:
    @pytest.mark.usefixtures("add_user")
    @pytest.mark.parametrize(("email", "password"), [("test_email@yandex.ru", "qwerty")])
    def test_refresh_token(self, client: TestClient, email, password):
        auth_result = client.post(
            "/auth/api/v1/account/login",
            json={
                "email": email,
                "password": password,
            },
        )
        account_id = auth_result.json().get("id")

        result = client.get(
            "/auth/api/v1/account/refresh_tokens", cookies={"refresh_token": auth_result.cookies.get("refresh_token")}
        )

        assert result.status_code == HTTPStatus.NO_CONTENT
        assert result.text == ""

        check_jwt_tokens(result.cookies, account_id)


class TestLoginHistory:
    @pytest.mark.usefixtures("add_user")
    @pytest.mark.parametrize(("email", "password"), [("test_login_history@yandex.ru", "qwerty")])
    def test_login_history(self, client: TestClient, email, password):
        for _ in range(5):
            client.post(
                "/auth/api/v1/account/login",
                json={
                    "email": email,
                    "password": password,
                },
            )

        result = client.get("/auth/api/v1/account/login_history")
        result_dict = result.json()

        assert result.status_code == HTTPStatus.OK

        assert len(result_dict) == 5
        assert result_dict[0].get("id")
        assert result_dict[0].get("userAgent")
        assert result_dict[0].get("loginTime")
