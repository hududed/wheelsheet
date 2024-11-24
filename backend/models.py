from datetime import datetime

from sqlmodel import Field, SQLModel


class Order(SQLModel, table=True):
    created_at: datetime
    account_number: str = Field(nullable=False)
    chain_symbol: str
    expiration_date: datetime
    strike_price: float
    net_amount: float
    net_amount_direction: str
    quantity: float
    state: str
