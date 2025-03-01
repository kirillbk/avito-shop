from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt


class ErrorResponse(BaseModel):
    errors: str


class UserItemSchema(BaseModel):
    type: str
    quantity: PositiveInt


class UserReceivedSchema(BaseModel):
    fromUser: str = Field(validation_alias="name")
    amount: PositiveInt


class UserSentSchema(BaseModel):
    toUser: str = Field(validation_alias="name")
    amount: PositiveInt


class CoinHistorySchema(BaseModel):
    received: list[UserReceivedSchema]
    sent: list[UserSentSchema]


class InfoResponse(BaseModel):
    coins: NonNegativeInt
    inventory: list[UserItemSchema]
    coinHistory: CoinHistorySchema


class SendCoinRequest(BaseModel):
    toUser: str
    amount: NonNegativeInt


class AuthRequest(BaseModel):
    username: str = Field(min_length=1, max_length=256)
    password: str = Field(min_length=8, max_length=256)


class AuthResponse(BaseModel):
    token: str
