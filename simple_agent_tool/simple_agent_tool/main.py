"""Entry point for the simplified agentic development tool."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .router import router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(title="Archon Lite - Agentic Dev Tool")

    templates_path = Path(__file__).parent / "templates"
    static_path = Path(__file__).parent / "static"
    templates = Jinja2Templates(directory=str(templates_path))

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse("index.html", {"request": request})

    app.include_router(router, prefix="/api")
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover - manual launch helper
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
