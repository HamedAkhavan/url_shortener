import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class IPMonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        response = await call_next(request)
        logger.info(
            "============ IP %s accessed code: %s",
            client_ip,
            request.url.path,
        )
        return response
