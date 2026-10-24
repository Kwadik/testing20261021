from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import get_session
from app.main import app
from app.services.categories import (
    CategoryCycleError,
    CategoryNotFoundError,
    CategorySlugConflictError,
)

CATEGORY_ID = UUID("43c30a75-b157-4844-a838-b8d1faf9a9b3")


async def override_get_session():
    yield object()


@pytest_asyncio.fixture
async def client():
    app.dependency_overrides[get_session] = override_get_session
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_session, None)


@pytest.mark.asyncio
async def test_create_category_with_missing_parent_returns_404(
    client, monkeypatch
):
    async def fake_create_category(session, data):
        raise CategoryNotFoundError("Parent category not found")

    monkeypatch.setattr(
        "app.api.categories.create_category",
        fake_create_category,
    )

    response = await client.post(
        "/api/v1/categories",
        json={
            "name": "Child",
            "slug": f"child-{uuid4().hex}",
            "parent_id": str(uuid4()),
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Parent category not found"}


@pytest.mark.asyncio
async def test_duplicate_slug_returns_409(client, monkeypatch):
    async def fake_create_category(session, data):
        raise CategorySlugConflictError

    monkeypatch.setattr(
        "app.api.categories.create_category",
        fake_create_category,
    )

    response = await client.post(
        "/api/v1/categories",
        json={
            "name": "Duplicate",
            "slug": f"duplicate-{uuid4().hex}",
        },
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Category slug already exists"}


@pytest.mark.asyncio
async def test_category_cannot_be_its_own_parent(client, monkeypatch):
    async def fake_update_category(session, category_id, changes):
        raise CategoryCycleError

    monkeypatch.setattr(
        "app.api.categories.update_category",
        fake_update_category,
    )

    response = await client.patch(
        f"/api/v1/categories/{CATEGORY_ID}",
        json={"parent_id": str(CATEGORY_ID)},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Category cannot be its own ancestor"
    }


@pytest.mark.asyncio
async def test_update_category_with_missing_parent_returns_404(
    client, monkeypatch
):
    async def fake_update_category(session, category_id, changes):
        raise CategoryNotFoundError("Parent category not found")

    monkeypatch.setattr(
        "app.api.categories.update_category",
        fake_update_category,
    )

    response = await client.patch(
        f"/api/v1/categories/{CATEGORY_ID}",
        json={"parent_id": str(uuid4())},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Parent category not found"}
