from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.core.config import get_settings
from app.core.security import verify_meta_signature
from app.services.meta import normalize_meta_events
from app.services.orchestrator import Orchestrator, build_orchestrator

router = APIRouter()
logger = logging.getLogger(__name__)


def get_orchestrator() -> Orchestrator:
    return build_orchestrator()


@router.get("/webhook/meta")
async def meta_verify(request: Request) -> Response:
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    settings = get_settings()
    if mode == "subscribe" and token == settings.meta_verify_token:
        return Response(content=challenge or "", media_type="text/plain")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification failed")


@router.post("/webhook/meta")
async def meta_webhook(
    request: Request,
    orchestrator: Orchestrator = Depends(get_orchestrator),
) -> dict[str, str]:
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    if not verify_meta_signature(raw_body, signature):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature")

    try:
        payload: Any = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError:
        logger.warning("Invalid JSON payload from Meta")
        return {"status": "ignored"}

    events = normalize_meta_events(payload)
    for event in events:
        await orchestrator.process_message(event["platform"], event["sender_id"], event["text"])
    return {"status": "ok"}
