import os
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from app.models.category import Category
from app.models.product import Product
from app.repositories.product import get_active_products


@pytest_asyncio.fixture
async def db_session():
    database_url = os.environ.get("TEST_DATABASE_URL")
    if not database_url:
        pytest.fail("Set TEST_DATABASE_URL to the isolated shop_test database")

    if not database_url.endswith("/shop_test"):
        pytest.fail("Integration tests may only use the shop_test database")

    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    try:
        async with session_factory() as session:
            await session.begin()
            try:
                yield session
            finally:
                await session.rollback()
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_category_filter_includes_descendants(db_session):
    suffix = uuid4().hex

    parent = Category(
        name=f"Test parent {suffix}",
        slug=f"test-parent-{suffix}",
    )
    child = Category(
        name=f"Test child {suffix}",
        slug=f"test-child-{suffix}",
        parent=parent,
    )
    grandchild = Category(
        name=f"Test grandchild {suffix}",
        slug=f"test-grandchild-{suffix}",
        parent=child,
    )
    unrelated = Category(
        name=f"Test unrelated {suffix}",
        slug=f"test-unrelated-{suffix}",
    )

    db_session.add_all([parent, child, grandchild, unrelated])
    await db_session.flush()

    parent_product = Product(
        title=f"Parent product {suffix}",
        category_id=parent.id,
        is_active=True,
    )
    child_product = Product(
        title=f"Child product {suffix}",
        category_id=child.id,
        is_active=True,
    )
    grandchild_product = Product(
        title=f"Grandchild product {suffix}",
        category_id=grandchild.id,
        is_active=True,
    )
    unrelated_product = Product(
        title=f"Unrelated product {suffix}",
        category_id=unrelated.id,
        is_active=True,
    )
    inactive_product = Product(
        title=f"Inactive product {suffix}",
        category_id=child.id,
        is_active=False,
    )

    db_session.add_all([
        parent_product,
        child_product,
        grandchild_product,
        unrelated_product,
        inactive_product,
    ])
    await db_session.flush()

    products = await get_active_products(
        db_session,
        category_id=parent.id,
    )

    actual_ids = {product.id for product in products}
    expected_ids = {
        parent_product.id,
        child_product.id,
        grandchild_product.id,
    }

    assert actual_ids == expected_ids
