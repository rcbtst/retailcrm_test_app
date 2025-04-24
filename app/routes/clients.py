from typing import Annotated
from fastapi import APIRouter, Query

from app.dependencies import RetailCRM_API_Client_Dep
from app.models import (
    GetClientsRequest,
    CreatedClientResponse,
    CreateClientRequest,
    PaginatedRequest,
    GetClientOrdersRequest,
    GetClientOrdersResponse,
    GetClientsResponse,
)


router = APIRouter(
    prefix="/clients",
    tags=["clients"],
)


@router.get("", response_model=GetClientsResponse)
async def get_clients(
    retailcrm_api_client: RetailCRM_API_Client_Dep,
    filter_query: Annotated[GetClientsRequest, Query()],
):
    return await retailcrm_api_client.get_clients(filter_query)


@router.post("", response_model=CreatedClientResponse)
async def create_client(
    retailcrm_api_client: RetailCRM_API_Client_Dep, request_data: CreateClientRequest
):
    return await retailcrm_api_client.create_client(request_data)


@router.get("/{client_id}/orders", response_model=GetClientOrdersResponse)
async def get_client_orders(
    retailcrm_api_client: RetailCRM_API_Client_Dep,
    client_id: int,
    pagination: Annotated[PaginatedRequest, Query()],
):
    return await retailcrm_api_client.get_client_orders(
        GetClientOrdersRequest(client_id=client_id, **pagination.dict())
    )
