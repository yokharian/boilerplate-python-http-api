"""
more uvicorn options here https://www.uvicorn.org/#command-line-options
you must translate to snake_case and insert to 'uvicorn.run(' below,
i.e: implement log-level
--log-level="warning"  ---> log_level="warning"
if you want exact kwargs signature, read Config class from uvicorn:
from uvicorn import Config

Have Fun 😁
"""
import uvicorn

if __name__ == "__main__":
    # (log_level='warning') disables loading logs, but
    # actual microservice logging is defined through the follow env var:
    # environ["LOGURU_LEVEL"] = "INFO"
    uvicorn.run(app="app:app", port=8080, log_level="warning", host="0.0.0.0")
