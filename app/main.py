from __future__ import annotations

import logging
from typing import Awaitable, Callable

from fastapi import FastAPI, Request, Response

from app.core.logging import get_request_id, log_request, log_response, setup_logging
from app.routers.health import router as health_router
from app.routers.meta import router as meta_router
from app.routers.telegram import router as telegram_router
from app.storage.db import engine
from app.storage.models import Base

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Appointment Bot", version="1.0.0")


@app.middleware("http")
async def request_logger(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    request_id = get_request_id()
    await log_request(request, {"request_id": request_id})
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    await log_response(request, response.status_code, {"request_id": request_id})
    return response


@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(health_router)
app.include_router(meta_router)
app.include_router(telegram_router)
