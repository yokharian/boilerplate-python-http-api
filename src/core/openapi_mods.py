import json
from typing import Any, Dict, Optional

from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi
from starlette.responses import HTMLResponse


def custom_openapi(app: Any):
    """https://fastapi.tiangolo.com/advanced/extending-openapi"""
    if app.openapi_schema:  # cache
        return app.openapi_schema
    try:
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
            tags=app.openapi_tags,
            servers=app.servers,
            terms_of_service=app.terms_of_service,
            contact=app.contact,
            license_info=app.license_info,
        )
    except Exception as e:
        raise SyntaxError(
            "invalid openapi_schema, maybe conflict with endpoints"
        ) from e
    openapi_schema["info"]["x-logo"] = {"url": "static/logo.png"}
    app.openapi_schema = openapi_schema
    app.openapi = custom_openapi
    if not app.openapi_schema.get("components"):
        app.openapi_schema["components"] = {"schemas": {}}
    app.openapi_schema["components"]["schemas"]["HTTPValidationError"] = {
        "title": "HTTPValidationError",
        "type": "object",
        "properties": {"errors": {"$ref": "#/components/schemas/ValidationError"}},
    }
    app.openapi_schema["components"]["schemas"]["ValidationError"] = {
        "title": "ValidationError",
        "required": ["errors"],
        "type": "object",
        "properties": {},
    }
    return lambda *a, **kw: app.openapi_schema


def get_swagger_ui_html(
    *,
    openapi_url: str,
    title: str,
    swagger_js_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js",
    swagger_css_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css",
    swagger_favicon_url: str = "https://fastapi.tiangolo.com/img/favicon.png",
    oauth2_redirect_url: Optional[str] = None,
    init_oauth: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> HTMLResponse:
    """custom swagger html function made to remove section of schemas
    with the parameter defaultModelsExpandDepth: -1"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="{swagger_css_url}">
    <link rel="shortcut icon" href="{swagger_favicon_url}">
    <title>{title}</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="{swagger_js_url}"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({{
        url: '{openapi_url}',
    """

    if oauth2_redirect_url:
        html += f"oauth2RedirectUrl: window.location.origin + '{oauth2_redirect_url}',"

    # https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/
    html += """
        dom_id: '#swagger-ui',
        presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
        layout: "BaseLayout",
        deepLinking: true,
        showExtensions: true,
        showCommonExtensions: true,
        defaultModelsExpandDepth: -1
    })"""

    if init_oauth:
        html += f"""
        ui.initOAuth({json.dumps(jsonable_encoder(init_oauth))})
        """

    html += """
    </script>
    </body>
    </html>
    """
    return HTMLResponse(html)
