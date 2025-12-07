import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, NoResultFound

from apps.urls.api import v1_shortener_router
from core.middlewares import IPMonitoringMiddleware
from core.settings import settings, setup_logging
from core.utils import add_routers_to_app

logger = logging.getLogger(__name__)
setup_logging(settings.log_level)

app = FastAPI(
    docs_url=f"{settings.root_path}/docs",
    openapi_url=f"{settings.root_path}/openapi.json",
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(IPMonitoringMiddleware)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    if settings.debug:
        return JSONResponse(status_code=500, content={"detail": str(exc)})

    logger.exception(f"Unhandled exception occurred: {exc}")
    return JSONResponse(
        status_code=500, content={"detail": "An unexpected error occurred!"}
    )


@app.exception_handler(IntegrityError)
async def integrity_errir_exception_handler(request: Request, exc: IntegrityError):
    if settings.debug:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    logger.exception(f"Unhandled exception occurred: {exc}")
    return JSONResponse(status_code=400, content={"detail": "Invalid data!"})


@app.exception_handler(NoResultFound)
async def no_result_found_exception_handler(request: Request, exc: NoResultFound):
    if settings.debug:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    logger.exception(f"Unhandled exception occurred: {exc}")
    return JSONResponse(status_code=400, content={"detail": "No result found!"})


add_routers_to_app(
    routers=[
        ["", v1_shortener_router],
    ],
    app=app,
    root_path=settings.root_path,
)


@app.get(f"{settings.root_path}/ping")
def read_root():
    """
    Ping
    """
    return {"ping": True}
