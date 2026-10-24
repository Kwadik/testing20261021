from uuid import UUID

import pytest
from pydantic import ValidationError

from app.schemas.product import ProductCreate


TEST_CATEGORY_ID = UUID("00000000-0000-0000-0000-000000000001")

def test_title_is_trimmed():
    product = ProductCreate(category_id=TEST_CATEGORY_ID, title="  Кружка  ")

    assert product.title == "Кружка"


@pytest.mark.parametrize("title", ["", " ", "   \t  "])
def test_empty_title_is_rejected(title):
    with pytest.raises(ValidationError):
        ProductCreate(category_id=TEST_CATEGORY_ID, title=title)


def test_description_is_trimmed():
    product = ProductCreate(
        category_id=TEST_CATEGORY_ID,
        title="Кружка",
        description="  Для тестов  ",
    )

    assert product.description == "Для тестов"


def test_blank_description_becomes_none():
    product = ProductCreate(
        category_id=TEST_CATEGORY_ID,
        title="Кружка",
        description="   ",
    )

    assert product.description is None


@pytest.mark.parametrize("price", ["-1", "-0.01"])
def test_negative_price_is_rejected(price):
    with pytest.raises(ValidationError):
        ProductCreate(category_id=TEST_CATEGORY_ID, title="Кружка", price=price)


def test_price_with_more_than_two_decimal_places_is_rejected():
    with pytest.raises(ValidationError):
        ProductCreate(category_id=TEST_CATEGORY_ID, title="Кружка", price="10.999")


def test_currency_is_normalized():
    product = ProductCreate(
        category_id=TEST_CATEGORY_ID,
        title="Кружка",
        currency=" usd ",
    )

    assert product.currency == "USD"


def test_currency_with_invalid_length_is_rejected():
    with pytest.raises(ValidationError):
        ProductCreate(category_id=TEST_CATEGORY_ID, title="Кружка", currency="US")

def test_category_id_can_be_omitted():
    product = ProductCreate(title="Кружка")

    assert product.category_id is None