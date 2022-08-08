from typing import Optional

from fastapi import HTTPException, Request

from .. import router
from ...core.response_models import done, error


@router.get("/request_context")
@router.get("/aws_context")
async def obtain_aws_context_special_parameters(request: Request):
    """Get the context for the request."""
    if "aws_context" not in request.scope["path"]:
        return done(**dict(request))
    context = request.scope.get("aws.context")
    event = request.scope.get("aws.event")

    if not context or not event:
        return error("you are not in the AWS environment")
    return {
        "aws_event": event,
        "aws_context": {
            "function_name": context.function_name,
            "function_version": context.function_version,
            "invoked_function_arn": context.invoked_function_arn,
            "memory_limit_in_mb": context.memory_limit_in_mb,
            "aws_request_id": context.aws_request_id,
            "log_group_name": context.log_group_name,
        },
    }


@router.get("/raise_an_exception")
def this_will_raise_an_exception_automatically(
    status_code: Optional[int] = 500,
    python_native_exception: bool = True,
    detail: str = "an expected exception !",
):
    """
    Raise an HTTPException if we re're running Python - natively.

    Args:
        status_code: write your description
        python_native_exception: write your description
        detail: write your description
    """
    if python_native_exception:
        if status_code != 500:
            return done("you can't specify status code with native exception")
        raise ValueError(detail)

    raise HTTPException(status_code=status_code, detail=detail)
