from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate


async def create_order(
    session: AsyncSession,
    data: OrderCreate,
) -> Order:
    product_ids = [item.product_id for item in data.items]

    try:
        result = await session.scalars(
            select(Product)
            .where(
                Product.id.in_(product_ids),
                Product.is_active.is_(True),
            )
            .with_for_update()
        )
        products = {product.id: product for product in result.all()}

        if len(products) != len(product_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more products are unavailable",
            )

        currencies = set()
        total = Decimal("0.00")

        for item in data.items:
            product = products[item.product_id]

            if product.price is None or product.currency is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product '{product.title}' has no price configured",
                )

            if product.price < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product price is invalid",
                )

            currencies.add(product.currency.upper())
            total += product.price * item.quantity

        if len(currencies) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All products in an order must use the same currency",
            )

        order = Order(
            customer_name=data.customer_name,
            customer_contact=data.customer_contact,
            status="new",
            total_amount=total,
            currency=currencies.pop(),
        )

        order.items = [
            OrderItem(
                product_id=item.product_id,
                product_title=products[item.product_id].title,
                quantity=item.quantity,
                unit_price=products[item.product_id].price,
            )
            for item in data.items
        ]

        session.add(order)
        await session.commit()
        await session.refresh(order)
        await session.refresh(order, attribute_names=["items"])
        return order

    except Exception:
        await session.rollback()
        raise
