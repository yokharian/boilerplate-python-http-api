import decimal
from collections import defaultdict
from datetime import date, datetime
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import orjson as fastapi_orjson
from orjson import (
    OPT_OMIT_MICROSECONDS,
    OPT_SERIALIZE_NUMPY,
    OPT_SERIALIZE_UUID,
    orjson,
)

ORIGINAL_ORJSON_DUMPS = orjson.dumps
DEFAULT_ORJSON_OPTIONS = (
    OPT_SERIALIZE_NUMPY | OPT_SERIALIZE_UUID | OPT_OMIT_MICROSECONDS
)


def json_serial(obj, safe=True):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, bytes):
        return obj.decode()
    else:
        for encoder in jsonable_encoder, str:
            try:
                return encoder(obj)
            except Exception:
                continue

    if safe:
        return "(ANY ?) Couldn't serialize this obj."

    not_serializable = TypeError(f"Type {type(obj)} isn't serializable")
    raise not_serializable


def _custom_new_default_orjson_dumps(content_or_obj: Any, **kwargs):
    """
    Create a new ORJSON dumps object with the default options.

    Args:
        content_or_obj: write your description
    """
    kwargs = defaultdict(**kwargs)
    kwargs.setdefault("default", json_serial)
    kwargs.setdefault("option", DEFAULT_ORJSON_OPTIONS)
    # always enable (ORJSON_OPTS) through (Bitwise OR) operator
    kwargs["option"] |= DEFAULT_ORJSON_OPTIONS
    return ORIGINAL_ORJSON_DUMPS(content_or_obj, **kwargs)


# extend its functionality placing default settings
orjson.dumps = fastapi_orjson.dumps = _custom_new_default_orjson_dumps
