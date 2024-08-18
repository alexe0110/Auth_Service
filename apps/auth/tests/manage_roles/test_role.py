import uuid
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient


class TestGetRole:
    @pytest.mark.kek()
    @pytest.mark.parametrize(
        ("role_id", "name"),
        [
            ("853a5a98-4dc4-4fc5-a95d-9a17c8ef7635", "ADMIN"),
            ("12891149-54d1-4b77-a198-1fad074e0213", "PORTAL_USER"),
        ],
    )
    def test_get_role_by_id(self, client: TestClient, role_id, name):
        result = client.get(f"/api/v1/role/{role_id}")
        result_dict = result.json()

        assert result.status_code == HTTPStatus.OK
        assert result_dict.get("id") == role_id
        assert result_dict.get("name") == name

    def test_get_not_exist_role(self, client: TestClient):
        result = client.get(f"/api/v1/role/{uuid.uuid4()}")
        result_dict = result.json()

        assert result.status_code == HTTPStatus.NOT_FOUND
        assert result_dict.get("detail") == "Role not found"

    def test_get_all_roles(self, client: TestClient):
        result = client.get("/api/v1/role/")
        result_dict = result.json()

        assert result.status_code == HTTPStatus.OK
        assert isinstance(result_dict, list)


class TestCreateRole:
    def test_create_role(self, client: TestClient):
        result = client.post("/api/v1/role/", json={"name": "Manager"})
        result_dict = result.json()

        assert result.status_code == HTTPStatus.OK
        assert result_dict.get("id")
        assert result_dict.get("name") == "Manager"

    def test_create_exist_role(self, client: TestClient):
        result = client.post("/api/v1/role/", json={"name": "ADMIN"})
        result_dict = result.json()

        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert result_dict.get("detail") == "Role already exist"


class TestUpdateRole:
    def test_update_role(self, client: TestClient, add_role):
        created_role_id = add_role

        result = client.patch(f"/api/v1/role/{created_role_id}", json={"new_name": "Reader"})
        result_dict = result.json()

        assert result.status_code == HTTPStatus.OK

        assert result_dict.get("id") == created_role_id
        assert result_dict.get("name") == "Reader"


class TestDeleteRole:
    def test_delete_role(self, client: TestClient, add_role):
        created_role_id = add_role

        result = client.delete(f"/api/v1/role/{created_role_id}")
        result_dict = result.json()

        assert result.status_code == HTTPStatus.OK
        assert result_dict.get("detail") == f"Role {created_role_id} was be deleted"

    def test_delete_not_exist(self, client: TestClient):
        not_created_role_id = uuid.uuid4()

        result = client.delete(f"/api/v1/role/{not_created_role_id}")
        result_dict = result.json()

        assert result.status_code == HTTPStatus.NOT_FOUND
        assert result_dict.get("detail") == "Role not found"
