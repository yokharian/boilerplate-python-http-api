import json
from typing import Callable, TypeVar, Union

from fastapi.routing import APIRoute
from fastapi import Request
from loguru import logger
from starlette.datastructures import Headers
from starlette.middleware.cors import CORSMiddleware as OGCORSMiddleware
from fastapi.responses import ORJSONResponse
from starlette.responses import Response
from starlette.status import (
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from fastapi.exceptions import RequestValidationError
from starlette.routing import Match
from starlette.types import Receive, Scope, Send
from .config import HEADERS

ResponseVar = TypeVar("ResponseVar", bound=Response)


def add_needed_headers(response: ResponseVar) -> ResponseVar:
    """using this method as all CORS middlewares found buggy
    make sure to use in (exception handlers) too, and any other 'interceptor'
    """
    response.headers.update(HEADERS)
    return response


async def error_500_handler(
    request: Request, exc: Union[BaseException, RuntimeError, Exception]
) -> ORJSONResponse:
    """Handle HTTP 500 Internal Server Error."""
    response = ORJSONResponse(
        {"detail": exc.__str__()},
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    )
    return add_needed_headers(response)


async def error_422_handler(
    request: Request, exc: RequestValidationError
) -> ORJSONResponse:
    """Handler for 422 error to transform default pydantic error object to
    more easy-to-read format"""
    errors = {}
    for error in exc.errors():  # remove 'body' from path to invalid element
        error_name = ".".join(map(str, error["loc"][1:]))
        errors[error_name] = error["msg"]
    response = ORJSONResponse(
        {"errors": errors}, status_code=HTTP_422_UNPROCESSABLE_ENTITY
    )
    return add_needed_headers(response)


class CORSMiddleware(OGCORSMiddleware):
    def __init__(self, add_response_headers: dict, **kwargs):
        """
        Add response headers.

        Args:
            add_response_headers: write your description
        """
        super().__init__(**kwargs)
        self.simple_headers.update(add_response_headers)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Add headers to the origin if not already present.

        Args:
          scope: write your description
          receive: write your description
          send: write your description
        """
        if scope["type"] != "http":  # pragma: no cover
            await self.app(scope, receive, send)
            return

        # fake the origin to bypass validation & add headers
        if "origin" not in Headers(scope=scope):
            scope["headers"] += [(b"origin", b"localhost")]

        return await super().__call__(scope, receive, send)


async def log_relevant_request_info(request: Request, response: Response) -> None:
    """Catch all requests to log relevant information inside a request

    - Using fastapi.Depends instead of middleware because of
    https://github.com/tiangolo/fastapi/issues/394
    """
    try:
        logger.info(f"{request.method} | {request.url.path}")

        # obtain route matching actual scope
        _route = (i.matches(request) for i in request.app.router.routes)
        _route = (scope for match, scope in _route if match == Match.FULL)
        scope = next(_route)

        if path_params := dict(scope["path_params"]):
            logger.info(f"{path_params=}")
        if query_params := dict(request.query_params):
            logger.info(f"{query_params=}")
        if headers := dict(request.headers):
            logger.debug(f"{headers=}")

        # this specific line, must be implemented with fastapi.Depends
        # https://github.com/tiangolo/fastapi/issues/394
        if request_body := await request.body():
            try:  # if json compact it
                request_body = json.dumps(json.loads(request_body))
                request_body = "".join(filter(str.isprintable, request_body))
            except Exception as e:
                logger.exception(e)
            logger.info(f"RequestBody:\n{request_body}")
    except Exception as e:  # avoid unknown errors, keep the request flow
        logger.exception(e)


class LogResponseStatusCode(APIRoute):
    def get_route_handler(self) -> Callable:
        """
        Overrides the default route handler to catch and log exceptions.

        Args:
            self: write your description
        """
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            """
            Custom route handler that logs exceptions.

            Args:
              request: original request
            """
            try:
                response: Response = await original_route_handler(request)
            except BaseException as e:
                if isinstance(e, RequestValidationError):
                    logger.error("response.status_code=422")  # default code
                else:
                    status_code = getattr(e, "status_code", 500)
                    logger.error(f"response.status_code={status_code}")

                # noinspection PyBroadException
                try:  # make exception printable (avoid \n and \t)
                    _printable = filter(str.isprintable, e.__repr__())
                    e.__str__ = lambda *a, **kw: "".join(_printable)
                except Exception:
                    ...
                finally:
                    raise e from None
            else:
                logger.info(f"{response.status_code=}")
                return response

        return custom_route_handler
