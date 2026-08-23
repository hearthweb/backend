from fastapi import status
from fastapi.testclient import TestClient

from app.models.registry.category import (
    Category,
    CategoryRead,
)
from app.models.user import User
from tests.utils import compare_sorted, dump


def test_registry_categories(
    client: TestClient,
    logged_in_admin: User,
    category: Category,
):
    response = client.get("/registry/categories")
    assert response.status_code == status.HTTP_200_OK
    assert compare_sorted(
        response.json(),
        [
            dump(CategoryRead, category),
        ],
        "id",
    )
