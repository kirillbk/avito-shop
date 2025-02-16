from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    server_port: int

    jwt_secret_key: str
    jwt_token_expire_minutes: int
    jwt_algorithm: str

    postgres_host: str
    postgres_port: str
    postgres_db: str
    postgres_user: str
    postgres_password: str

    debug: bool = False


settings = Settings()
