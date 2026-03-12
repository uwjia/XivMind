import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from loguru import logger


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        
        with logger.contextualize(request_id=request_id):
            logger.bind(request_id=request_id).debug(
                f"Request started: {request.method} {request.url.path}"
            )
            
            response = await call_next(request)
            
            response.headers["X-Request-ID"] = request_id
            
            logger.bind(request_id=request_id).debug(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}"
            )
            
        return response
