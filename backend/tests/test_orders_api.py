from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import get_session
from app.main import app


class FakeSession:
    def __init__(self):
        self.added = []
        self.committed = False
        self.rolled_back = False

    def add(self, obj):
        self.added.append(obj)

    async def commit(self):
        from datetime import datetime, timezone
        from uuid import uuid4

        self.committed = True
        for obj in self.added:
            if hasattr(obj, "items"):
                obj.id = uuid4()
                obj.created_at = datetime.now(timezone.utc)
                for item in obj.items:
                    item.id = uuid4()
                    item.order = obj

    async def refresh(self, obj, attribute_names=None):
        return None

    async def rollback(self):
        self.rolled_back = True

    async def scalars(self, statement):
        return SimpleNamespace(all=lambda: self.products)


@pytest_asyncio.fixture
async def client():
    session = FakeSession()

    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as test_client:
            yield test_client, session
    finally:
        app.dependency_overrides.pop(get_session, None)


@pytest.mark.asyncio
async def test_create_order_calculates_total_from_database(client, monkeypatch):
    test_client, session = client
    product_id = uuid4()
    session.products = [
        SimpleNamespace(
            id=product_id,
            title="Кружка",
            price=Decimal("125.50"),
            currency="PLN",
            is_active=True,
        )
    ]

    response = await test_client.post(
        "/api/v1/orders",
        json={
            "customer_name": "Иван",
            "customer_contact": "@ivan",
            "items": [{"product_id": str(product_id), "quantity": 2}],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["total_amount"] == "251.00"
    assert body["currency"] == "PLN"
    assert body["status"] == "new"
    assert body["items"][0]["product_title"] == "Кружка"
    assert body["items"][0]["unit_price"] == "125.50"
    assert session.committed is True


@pytest.mark.asyncio
async def test_create_order_rejects_unavailable_product(client):
    test_client, session = client
    session.products = []

    response = await test_client.post(
        "/api/v1/orders",
        json={
            "customer_name": "Иван",
            "customer_contact": "@ivan",
            "items": [{"product_id": str(uuid4()), "quantity": 1}],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "One or more products are unavailable"
    assert session.committed is False
    assert session.rolled_back is True
