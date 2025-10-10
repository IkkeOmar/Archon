from __future__ import annotations

import logging
import sys
import uuid
from typing import Any, Dict

from fastapi import Request


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_request_id() -> str:
    return uuid.uuid4().hex


async def log_request(request: Request, extra: Dict[str, Any] | None = None) -> None:
    logger = logging.getLogger("app.request")
    payload: Dict[str, Any] = {
        "method": request.method,
        "path": request.url.path,
    }
    if extra:
        payload.update(extra)
    logger.info("request", extra={"props": payload})


async def log_response(request: Request, status_code: int, extra: Dict[str, Any] | None = None) -> None:
    logger = logging.getLogger("app.response")
    payload: Dict[str, Any] = {
        "method": request.method,
        "path": request.url.path,
        "status_code": status_code,
    }
    if extra:
        payload.update(extra)
    logger.info("response", extra={"props": payload})
