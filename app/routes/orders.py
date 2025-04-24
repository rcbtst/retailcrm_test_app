from fastapi import APIRouter

from app.dependencies import RetailCRM_API_Client_Dep
from app.models import (
    OrderCreateRequest,
    CreatedOrderResponse,
    CreateOrderPaymentRequest,
    CreatedOrderPaymentResponse,
)


router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


@router.post("", response_model=CreatedOrderResponse)
async def create_order(
    retailcrm_api_client: RetailCRM_API_Client_Dep, request_data: OrderCreateRequest
):
    return await retailcrm_api_client.create_order(request_data)


@router.post("/payments", response_model=CreatedOrderPaymentResponse)
async def attach_payment_to_order(
    retailcrm_api_client: RetailCRM_API_Client_Dep,
    request_data: CreateOrderPaymentRequest,
):
    return await retailcrm_api_client.create_order_payment(request_data)
