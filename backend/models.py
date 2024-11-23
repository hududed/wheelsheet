from sqlmodel import Field, SQLModel


class Order(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: str
    instrument: str
    quantity: int
    price: float
    state: str
