import re
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


REQUEST_ID_HEADER = "X-Request-ID"
MAX_REQUEST_ID_LENGTH = 128
VALID_REQUEST_ID = re.compile(r"^[\x21-\x7e]{1,128}$")


def make_request_id(value: str | None) -> str:
    if value and VALID_REQUEST_ID.fullmatch(value):
        return value
    return f"req_{uuid.uuid4().hex}"


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = make_request_id(request.headers.get(REQUEST_ID_HEADER))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response