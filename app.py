"""REST API BACKEND MICROSERVICE"""
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware import Middleware
from starlette.staticfiles import StaticFiles
from starlette.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
)
import fastapi.openapi.models
from loguru import logger

from src.core.swagger_utils import build_response
from src.core.custom_logger import custom_loguru_app_logger
from src.core.openapi_mods import (
    custom_openapi,
    get_swagger_ui_html as new_swagger,
)
from src import router as v1_router, tags_metadata
from src.core.config import HEADERS, PROJECT_NAME
from src.core.pre_after_requests import (
    CORSMiddleware,
    error_422_handler,
    error_500_handler,
    log_relevant_request_info,
)

HERE = Path(__file__).parent
STATICS_DIR = HERE.joinpath("static")

MOCKS_GENERAL = HERE.joinpath("api_default_mocks")
NOT_IN_DYNAMO = MOCKS_GENERAL.joinpath("mock_dynamo_not_found_500.json")
UNEXPECTED = MOCKS_GENERAL.joinpath("something_unexpected_happened_500.json")
FIELD_REQUIRED = MOCKS_GENERAL.joinpath("generic_model_field_required_422.json")
BAD_TYPE = MOCKS_GENERAL.joinpath("model_type_does_not_match_422.json")

app = FastAPI(
    title=PROJECT_NAME,
    version="v1",
    description=__doc__,
    docs_url="/",
    redoc_url="/docs",
    debug=False,  # True will cause pre&after requests just skip
    exception_handlers={
        HTTP_500_INTERNAL_SERVER_ERROR: error_500_handler,
        RequestValidationError: error_422_handler,
    },
    # contact={"name": "", "email": "", "url": ""},
    terms_of_service="",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=tags_metadata,
    default_response_class=ORJSONResponse,
    dependencies=[Depends(log_relevant_request_info)],
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            max_age=3600,
            add_response_headers=HEADERS,
        ),
    ],
    responses={
        **build_response(500, default=UNEXPECTED, not_found_in_db=NOT_IN_DYNAMO),
        **build_response(422, field_required=FIELD_REQUIRED, bad_type=BAD_TYPE),
    },
)

app.logger = custom_loguru_app_logger()  # disabling could disfigure logs
app.include_router(v1_router, prefix="/v1")  # MUST

try:  # try to customize fast-api app
    app.openapi = custom_openapi(app)
except Exception as e:  # they are just aesthetic changes
    logger.exception(e)

try:  # try to override swagger
    fastapi.applications.get_swagger_ui_html = new_swagger
except Exception as e:  # they are just aesthetic changes
    logger.exception(e)

try:  # try to mount static files (like images etc...)
    app.mount("/static", StaticFiles(directory=STATICS_DIR), name="static")
except Exception as e:  # shouldn't fail but this isn't essential
    logger.exception(e)
