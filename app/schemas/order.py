from pydantic import BaseModel


class OrderCreate(BaseModel):
    order_id: str
    amount: float
    user_id: str


class OrderOut(BaseModel):
    order_id: str
    amount: float
    status: str
    user_id: str

    class Config:
        from_attributes = True
