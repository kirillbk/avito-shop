from pydantic import BaseModel, Field, SecretStr, NonNegativeInt, PositiveInt


class ErrorResponse(BaseModel):
    errors: str


class ItemSchema(BaseModel):
    type: str
    quantity: PositiveInt


class ReceivedSchema(BaseModel):
    fromUser: str
    amount: PositiveInt


class SentSchema(BaseModel):
    toUser: str
    amount: PositiveInt


class coinHistorySchema(BaseModel):
    received: list[ReceivedSchema]
    sent: list[SentSchema]


class InfoResponse(BaseModel):
    coins: int
    inventory: list[ItemSchema]
    coinHistory: coinHistorySchema


class SendCoinRequest(BaseModel):
    toUser: str
    amount: NonNegativeInt


class AuthRequest(BaseModel):
    username: str = Field(min_length=1)
    password: SecretStr = Field(min_length=8)


class AuthResponse(BaseModel):
    token: str
