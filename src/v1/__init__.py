from fastapi import APIRouter

from ..core.pre_after_requests import LogResponseStatusCode

router = APIRouter(route_class=LogResponseStatusCode)
