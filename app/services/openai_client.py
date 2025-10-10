from __future__ import annotations

import json
import logging
from typing import Any, Dict

from openai import AsyncOpenAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class NLUClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key_value)
        self.model = settings.openai_model
        with open("app/llm/system.md", "r", encoding="utf-8") as fp:
            self.system_prompt = fp.read()

    async def parse(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.client.responses.create(  # type: ignore[attr-defined]
            model=self.model,
            temperature=0.1,
            response_format={"type": "json_object"},
            input=[
                {
                    "role": "system",
                    "content": self.system_prompt,
                },
                {
                    "role": "user",
                    "content": json.dumps({"message": message, "context": context}),
                },
            ],
        )
        output = response.output
        if not output:
            raise ValueError("Empty response from OpenAI")
        content = output[0].content[0].text
        return json.loads(content)


def build_nlu_client() -> NLUClient:
    return NLUClient()
