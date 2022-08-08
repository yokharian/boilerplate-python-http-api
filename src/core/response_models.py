"""https://fastapi.tiangolo.com/advanced/custom-response/?h=orjsonresponse"""
from typing import Any, Optional

from fastapi.responses import ORJSONResponse


def error(_error: Optional[Any] = None, **body):
    """
    Create a 400 error response.

    Args:
        _error: "error" description
        body: raw response here
    """
    final_body = {**body}
    if _error:
        final_body["error"] = _error
    return ORJSONResponse(dict(final_body), 400)


def invalid(_error: Optional[Any] = None, **body):
    """
    Create a 422 error response.

    Args:
        _error: "error" description
        body: raw response here
    """
    final_body = {**body}
    if _error:
        final_body["error"] = _error
    return ORJSONResponse(dict(final_body), 422)


def not_found(_error: Optional[Any] = None, **body):
    """
    Default 404 response

    Args:
        _error: response msg
        body: raw response here
    """
    final_body = {**body}
    if _error is not None:
        final_body["error"] = _error
    return ORJSONResponse(dict(final_body), 404)


def partial(**body):
    """
    Create a ORJSONResponse with status code 206.

    Args:
        body: raw response here
    """
    return ORJSONResponse(body, 206)


def done(_message: Optional[str] = None, **body):
    """
    Create a ORJSONResponse with status code 200.

    Args:
        _message: response msg
        body: raw response here
    """
    final_body = {**body}
    if _message is not None:
        final_body["message"] = _message
    return ORJSONResponse(dict(final_body), 200)


ok = done


def created(_created: Optional[Any] = None, **body):
    """
    Create a new resource.

    Args:
        _created: what have you created
        body: raw response here
    """
    final_body = {**body}
    if _created is not None:
        final_body["created"] = _created
    return ORJSONResponse(dict(final_body), 201)
