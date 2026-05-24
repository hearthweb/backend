from fastapi import status
from fastapi.testclient import TestClient

from app.models.user import User, UserRead


def test_get_users(client: TestClient, logged_in_user: User):
    response = client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert len(json) == 1
    assert json[0] == UserRead.model_validate(logged_in_user).model_dump(mode="json")
