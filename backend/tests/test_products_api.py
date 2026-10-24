from types import SimpleNamespace
from uuid import UUID

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import get_session
from app.main import app


CATEGORY_ID = UUID("43c30a75-b157-4844-a838-b8d1faf9a9b3")


async def override_get_session():
    # Эти тесты не обращаются к настоящей БД.
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
async def test_unknown_category_returns_404(client, monkeypatch):
    async def fake_get_category_by_id(session, category_id):
        return None

    async def unexpected_product_query(*args, **kwargs):
        pytest.fail("Products should not be queried for an unknown category")

    monkeypatch.setattr(
        "app.api.products.get_category_by_id",
        fake_get_category_by_id,
    )
    monkeypatch.setattr(
        "app.api.products.get_active_products",
        unexpected_product_query,
    )

    response = await client.get(
        "/api/v1/products",
        params={"category_id": str(CATEGORY_ID)},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Category not found"}


@pytest.mark.asyncio
async def test_existing_category_without_products_returns_empty_list(
    client,
    monkeypatch,
):
    received_category_ids = []

    async def fake_get_category_by_id(session, category_id):
        return SimpleNamespace(id=category_id)

    async def fake_get_active_products(session, category_id=None):
        received_category_ids.append(category_id)
        return []

    monkeypatch.setattr(
        "app.api.products.get_category_by_id",
        fake_get_category_by_id,
    )
    monkeypatch.setattr(
        "app.api.products.get_active_products",
        fake_get_active_products,
    )

    response = await client.get(
        "/api/v1/products",
        params={"category_id": str(CATEGORY_ID)},
    )

    assert response.status_code == 200
    assert response.json() == []
    assert received_category_ids == [CATEGORY_ID]