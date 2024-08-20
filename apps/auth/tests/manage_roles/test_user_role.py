import uuid
from http import HTTPStatus

from fastapi.testclient import TestClient


class TestUserRoleCreate:
    def test_user_role_create(self, client: TestClient, add_role, add_user):
        created_user_account_id = add_user
        created_role_id = add_role

        result = client.post(f"/auth/api/v1/account/{created_user_account_id}/roles", json=[created_role_id])
        result_dict = result.json()

        assert result.status_code == HTTPStatus.OK

        assert result_dict[0].get("id")
        assert result_dict[0].get("user_account_id") == created_user_account_id
        assert result_dict[0].get("role_id") == created_role_id

        result = client.post(f"/auth/api/v1/account/{created_user_account_id}/roles", json=[created_role_id])
        result_dict = result.json()

        assert result.status_code == HTTPStatus.CONFLICT
        assert result_dict.get("detail") == "User already have the specified role"

    def test_user_role_create_user_not_exist(self, client: TestClient, add_role):
        created_user_account_id = str(uuid.uuid4())
        created_role_id = add_role

        result = client.post(f"/auth/api/v1/account/{created_user_account_id}/roles", json=[created_role_id])
        result_dict = result.json()

        assert result.status_code == HTTPStatus.NOT_FOUND
        assert result_dict.get("detail") == "User not registered"

    def test_user_role_create_role_not_exist(self, client: TestClient, add_user):
        created_user_account_id = add_user
        created_role_id = str(uuid.uuid4())

        result = client.post(f"/auth/api/v1/account/{created_user_account_id}/roles", json=[created_role_id])
        result_dict = result.json()

        assert result.status_code == HTTPStatus.NOT_FOUND
        assert result_dict.get("detail") == "Role not exist"


class TestUserRoleDelete:
    def test_user_role_delete(self, client: TestClient, add_role, add_user):
        created_user_account_id = add_user
        created_role_id = add_role

        client.post(f"/auth/api/v1/account/{created_user_account_id}/roles", json=[created_role_id])

        result = client.delete(f"/auth/api/v1/account/{created_user_account_id}/roles/{created_role_id}")
        result_dict = result.json()

        assert result.status_code == HTTPStatus.OK
        assert len(result_dict) == 0

    def test_user_role_delete_not_exist(self, client: TestClient, add_user, add_role):
        created_user_account_id = add_user
        created_role_id = add_role

        result = client.delete(f"/auth/api/v1/account/{created_user_account_id}/roles/{created_role_id}")
        result_dict = result.json()

        assert result.status_code == HTTPStatus.NOT_FOUND
        assert result_dict.get("detail") == "User does not have the specified role"


class TestGetUserRoles:
    def test_get_user_roles(self, client: TestClient, add_role, add_user):
        created_user_account_id = add_user
        created_role_id = add_role

        client.post(f"/auth/api/v1/account/{created_user_account_id}/roles", json=[created_role_id])

        result = client.get(f"/auth/api/v1/account/{created_user_account_id}/roles")
        result_dict = result.json()

        assert result.status_code == HTTPStatus.OK
        assert len(result_dict) == 1

    def test_get_user_roles_not_exists_roles(self, client: TestClient, add_user):
        created_user_account_id = add_user

        result = client.get(f"/auth/api/v1/account/{created_user_account_id}/roles")
        result_dict = result.json()

        assert result.status_code == HTTPStatus.OK
        assert result_dict == []


class TestCheckUserRole:
    def test_check_user_role(self, client: TestClient, add_role, add_user):
        created_user_account_id = add_user
        created_role_id = add_role

        client.post(f"/auth/api/v1/account/{created_user_account_id}/roles", json=[created_role_id])

        result = client.get(f"/auth/api/v1/account/{created_user_account_id}/roles/{created_role_id}")

        assert result.status_code == HTTPStatus.NO_CONTENT
        assert result.text == ""

    def test_check_user_role_not_exist(self, client: TestClient, add_role, add_user):
        created_user_account_id = add_user
        created_role_id = add_role

        result = client.get(f"/auth/api/v1/account/{created_user_account_id}/roles/{created_role_id}")
        result_dict = result.json()

        assert result.status_code == HTTPStatus.NOT_FOUND
        assert result_dict.get("detail") == "User does not have the requested role"
