import logging
from http import HTTPStatus

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

logger = logging.getLogger("uvicorn.error")


def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    logger.info(str(exc))
    return JSONResponse({"errors": HTTPStatus(exc.status_code).phrase}, exc.status_code)


def system_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.info(exc)
    return JSONResponse(
        {"errors": HTTPStatus(status.HTTP_500_INTERNAL_SERVER_ERROR).phrase},
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def request_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    logger.info(exc)
    return JSONResponse(
        {"errors": HTTPStatus(status.HTTP_400_BAD_REQUEST).phrase},
        status.HTTP_400_BAD_REQUEST,
    )


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail)


class BadRequestException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail)
