from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session
from app.schemas.order import OrderCreate, OrderRead
from app.services.orders import create_order


router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@router.post(
    "",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_order_endpoint(
    data: OrderCreate,
    session: AsyncSession = Depends(get_session),
) -> OrderRead:
    return await create_order(session, data)
