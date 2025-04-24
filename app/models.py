from typing import Optional, Literal
from datetime import datetime, date
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    model_validator,
    ConfigDict,
)


class PaginatedRequest(BaseModel):
    page: Optional[int] = Field(default=1, description="Страница", ge=1)
    limit: Optional[Literal["20", "50", "100"]] = Field(
        default="20",
        description="Максимальное кол-во результатов на странице (20|50|100)",
    )


class Pagination(BaseModel):
    limit: int
    totalCount: int
    currentPage: int
    totalPageCount: int


class PaginatedResponse(BaseModel):
    pagination: Pagination


class Phone(BaseModel):
    number: str


class GetClientsRequest(PaginatedRequest):
    name: Optional[str] = Field(
        default=None,
        description="Фильтр по имени клиента",
        examples=["Иван"],
        max_length=255,
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="Фильтр по email",
        examples=["test@example.com"],
        max_length=255,
    )
    date_of_signup_from: Optional[date] = Field(
        default=None,
        description="Дата регистрации (от) (YYYY-MM-DD)",
        examples=["2023-01-21"],
    )
    date_of_signup_to: Optional[date] = Field(
        default=None,
        description="Дата регистрации (до) (YYYY-MM-DD)",
        examples=["2023-12-31"],
    )

    @model_validator(mode="before")
    def validate_dates(cls, values):
        date_from = values.get("date_of_signup_from")
        date_to = values.get("date_of_signup_to")

        if date_from and date_to:
            if date_from > date_to:
                raise ValueError(
                    "'date_of_signup_from' should be lower or equal to 'date_of_signup_to'"
                )

        return values


class CreateClientRequest(BaseModel):
    firstName: str = Field(
        description="Имя клиента",
        examples=["Иван"],
        max_length=255,
    )
    lastName: Optional[str] = Field(
        default=None,
        description="Фамилия клиента",
        examples=["Иванов"],
        max_length=255,
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="Email клиента",
        examples=["test@example.com"],
        max_length=255,
    )
    phones: Optional[list[Phone]] = Field(
        default_factory=list, description="Телефоны клиента"
    )
    externalId: Optional[str] = Field(default=None, description="Внешний ID клиента")
    isContact: Optional[bool] = Field(
        default=None, description="Клиент является контактным лицом"
    )


class CreatedClientResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int


class Client(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    type: str
    externalId: Optional[str] = None
    isContact: bool
    createdAt: datetime
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[EmailStr] = None
    phones: Optional[list[Phone]] = None


class GetClientsResponse(PaginatedResponse):
    model_config = ConfigDict(extra="ignore")

    clients: list[Client] = Field(alias="customers")


class OrderClientData(BaseModel):
    firstName: Optional[str] = Field(
        default=None,
        description="Имя клиента",
        examples=["Иван"],
        max_length=255,
    )
    lastName: Optional[str] = Field(
        default=None,
        description="Фамилия клиента",
        examples=["Иванов"],
        max_length=255,
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="Email клиента",
        examples=["test@example.com"],
        max_length=255,
    )
    phone: Optional[str] = None


class OrderItem(BaseModel):
    initialPrice: float
    productName: str


class OrderCreateRequest(BaseModel):
    number: str
    client_id: Optional[int] = None
    client_data: Optional[OrderClientData] = None
    items: list[OrderItem]

    @model_validator(mode="before")
    def validate_client(cls, values):
        client_id = values.get("client_id")
        client_data = values.get("client_data")

        if (client_id is None and client_data is None) or (
            client_id is not None and client_data is not None
        ):
            raise ValueError("Either 'client_id' or 'client_data' should be provided")

        return values


class CreatedOrderResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int


class Order(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    summ: Optional[float] = None
    currency: Optional[str] = None
    number: Optional[str] = None
    externalId: Optional[str] = None
    orderType: Optional[str] = None
    orderMethod: Optional[str] = None
    createdAt: datetime
    statusUpdatedAt: Optional[datetime] = None
    totalSumm: Optional[float] = None


class GetClientOrdersRequest(PaginatedRequest):
    client_id: int


class GetClientOrdersResponse(PaginatedResponse):
    model_config = ConfigDict(extra="ignore")

    orders: list[Order]


class CreateOrderPaymentRequest(BaseModel):
    order_id: int
    payment_amount: float
    payment_type: Literal["bank-card", "cash"] = "bank-card"
    payment_comment: Optional[str] = None


class CreatedOrderPaymentResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
