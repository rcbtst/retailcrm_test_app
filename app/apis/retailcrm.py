import logging
import json

import httpx
from aiolimiter import AsyncLimiter

from app.models import (
    GetClientsRequest,
    CreateClientRequest,
    CreatedClientResponse,
    OrderCreateRequest,
    CreatedOrderResponse,
    CreateOrderPaymentRequest,
    CreatedOrderPaymentResponse,
    GetClientOrdersRequest,
    GetClientsResponse,
    GetClientOrdersResponse,
)


logger = logging.getLogger(__name__)


class BaseRetailCRMAPIException(Exception):
    pass


class RequestFailedException(BaseRetailCRMAPIException):
    pass


class InvalidInputException(BaseRetailCRMAPIException):
    pass


class ServiceTemporaryUnavailableException(BaseRetailCRMAPIException):
    pass


class RetailCRM_API:
    def __init__(
        self,
        api_key: str,
        subdomain: str,
        api_version: str = "v5",
        rate_limit: tuple[int, int] | None = (10, 1),
        retries: int = 2,
    ):
        self.api_key = api_key
        self.subdomain = subdomain
        self.api_version = api_version
        self._client = httpx.AsyncClient(
            base_url=f"https://{subdomain}.retailcrm.ru/api/{api_version}/"
        )
        self.rate_limiter = (
            AsyncLimiter(max_rate=rate_limit[0], time_period=rate_limit[1])
            if rate_limit
            else None
        )
        self.retries = retries

    def _generate_auth_headers(self) -> dict[str, str]:
        return {
            "X-API-KEY": self.api_key,
        }

    def _drop_empty_request_data(self, data: dict) -> dict:
        return {k: v for k, v in data.items() if v is not None}

    def _prepare_query_data(self, query_data: dict | None) -> dict | None:
        if query_data:
            query_data = self._drop_empty_request_data(query_data)

        return query_data

    def _prepare_request_data(self, data: dict | None) -> dict | None:
        if data:
            data = self._drop_empty_request_data(data)
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    data[key] = json.dumps(value, ensure_ascii=False)

        return data

    async def _make_api_request(
        self,
        method: str,
        path: str,
        query_params: dict = None,
        data: dict = None,
        retries: int | None = None,
        **kwargs,
    ) -> dict:
        logger.info("Making RetailCRM API request '%s %s'", method, path)
        try:
            if self.rate_limiter is not None:
                async with self.rate_limiter:
                    pass

            request = self._client.build_request(
                method.upper(),
                path,
                headers=self._generate_auth_headers(),
                params=self._prepare_query_data(query_params),
                data=self._prepare_request_data(data),
                **kwargs,
            )
            response = await self._client.send(request)

            if response.status_code == 503:
                raise ServiceTemporaryUnavailableException

            response_data = response.json()
            response_success = response_data.get("success")
            response_error_msg = response_data.get("errorMsg", "")
            response_errors = response_data.get("errors", "")

            if response_success is None:
                raise BaseRetailCRMAPIException

            if response_success is False:
                if 400 <= response.status_code <= 499:
                    raise InvalidInputException(
                        f"{response_error_msg} {response_errors}"
                    )
                else:
                    raise RequestFailedException(
                        f"{response_error_msg} {response_errors}"
                    )

            return response_data
        except RequestFailedException:
            logger.exception("RetailCRM API request '%s %s' failed", method, path)
            raise
        except:
            if retries is None:
                retries = self.retries
            if retries:
                logger.exception(
                    "RetailCRM API request '%s %s' failed. Retrying...", method, path
                )
                retries -= 1
                return await self._make_api_request(
                    method, path, query_params, data, retries, **kwargs
                )
            else:
                logger.exception("RetailCRM API request '%s %s' failed", method, path)
                raise

    async def close(self):
        await self._client.aclose()

    async def get_clients(self, request: GetClientsRequest) -> GetClientsResponse:
        r = await self._make_api_request("get", "/reference/payment-types")
        print(r)

        response = await self._make_api_request(
            "GET",
            "/customers",
            query_params={
                "filter[name]": request.name,
                "filter[email]": request.email,
                "filter[dateFrom]": request.date_of_signup_from,
                "filter[dateTo]": request.date_of_signup_to,
                "page": request.page,
                "limit": request.limit,
            },
        )

        return GetClientsResponse(**response)

    async def create_client(
        self, request: CreateClientRequest
    ) -> CreatedClientResponse:
        customer_data = {
            "externalId": request.externalId,
            "isContact": request.isContact,
            "firstName": request.firstName,
            "lastName": request.lastName,
            "email": request.email,
            "phones": [phone.dict() for phone in request.phones],
        }

        response = await self._make_api_request(
            "POST",
            "/customers/create",
            data={
                "site": self.subdomain,
                "customer": customer_data,
            },
        )

        return CreatedClientResponse(**response)

    async def get_client_orders(
        self, request: GetClientOrdersRequest
    ) -> GetClientOrdersResponse:
        response = await self._make_api_request(
            "GET",
            "/orders",
            query_params={
                "page": request.page,
                "limit": request.limit,
                "filter[customerId]": request.client_id,
            },
        )

        return GetClientOrdersResponse(**response)

    async def create_order(self, request: OrderCreateRequest) -> CreatedOrderResponse:
        customer_data = {"id": request.client_id}
        order_data = {
            "number": request.number,
            "customer": customer_data,
            "firstName": request.client_data.firstName if request.client_data else None,
            "lastName": request.client_data.lastName if request.client_data else None,
            "email": request.client_data.email if request.client_data else None,
            "phone": request.client_data.phone if request.client_data else None,
            "items": [item.dict() for item in request.items],
        }

        response = await self._make_api_request(
            "POST",
            "/orders/create",
            data={
                "site": self.subdomain,
                "order": order_data,
            },
        )

        return CreatedOrderResponse(**response)

    async def create_order_payment(
        self, request: CreateOrderPaymentRequest
    ) -> CreatedOrderPaymentResponse:
        order_data = {"id": request.order_id}
        payment_data = {
            "amount": request.payment_amount,
            "comment": request.payment_comment,
            "order": order_data,
            "type": request.payment_type,
        }

        response = await self._make_api_request(
            "POST",
            "/orders/payments/create",
            data={
                "site": self.subdomain,
                "payment": payment_data,
            },
        )

        return CreatedOrderPaymentResponse(**response)
