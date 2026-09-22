from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.github.client import GitHubIntegrationError
from backend.routes.github_routes import router as github_router


app = FastAPI(
    title="Context Recovery GitHub Data Layer",
    version="0.1.0",
    description="GitHub integration and normalized project context collection.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(GitHubIntegrationError)
async def github_error_handler(request: Request, error: GitHubIntegrationError) -> JSONResponse:
    """Return safe, consistent HTTP errors for GitHub integration failures."""

    return JSONResponse(status_code=error.status_code, content={"detail": error.message})


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(github_router)

# Mount frontend static assets and serve SPA at root
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(str(frontend_dir / "index.html"))