"""FastAPI application for ResearchBot.

Exposes the single-page web UI, the non-sensitive health endpoint, and the
POST /ask endpoint that orchestrates the three-agent research workflow.
"""

import logging
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.agents.research_team import (
    ConfigurationError,
    ResearchTimeoutError,
    UpstreamServiceError,
    get_agent_names,
    run_research_workflow,
)
from app.agents.tools import get_library_stats
from app.config import APP_NAME, EDUCATIONAL_DISCLAIMER, get_settings
from app.schemas import AskRequest, AskResponse, ErrorResponse, HealthResponse

# Configure structured logging without logging credentials
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("researchbot")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title=APP_NAME,
    description="Educational multi-agent research assistant powered by FastAPI and Agno Team.",
    version="1.0.0",
)

# Enable CORS for local testing and deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory for CSS, JS, and assets
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic request validation errors cleanly."""
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    msg = first_error.get("msg", "Invalid request parameter.")
    # Clean up Pydantic prefix if present
    if msg.startswith("Value error, "):
        msg = msg.replace("Value error, ", "")

    logger.warning("Validation error on %s: %s", request.url.path, msg)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"status": "error", "message": msg, "detail": "Validation failed for request body."},
    )


@app.exception_handler(ConfigurationError)
async def configuration_exception_handler(request: Request, exc: ConfigurationError):
    """Handle missing or invalid configuration."""
    logger.error("Configuration error: %s", str(exc))
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "error", "message": str(exc), "detail": "Service configuration incomplete."},
    )


@app.exception_handler(ResearchTimeoutError)
async def timeout_exception_handler(request: Request, exc: ResearchTimeoutError):
    """Handle research execution timeout."""
    logger.error("Timeout during research: %s", str(exc))
    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content={"status": "error", "message": str(exc), "detail": "Request exceeded timeout."},
    )


@app.exception_handler(UpstreamServiceError)
async def upstream_exception_handler(request: Request, exc: UpstreamServiceError):
    """Handle upstream model or tool failures."""
    logger.error("Upstream error: %s", str(exc))
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"status": "error", "message": str(exc), "detail": "Upstream service error."},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all error handler preventing secret disclosure or raw trace leaks."""
    logger.exception("Unhandled server exception: %s", type(exc).__name__)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "An unexpected error occurred while processing your research request.",
            "detail": "Internal server error.",
        },
    )


@app.get("/", summary="Serve ResearchBot Web UI")
async def serve_index():
    """Serve the single-page application frontend."""
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frontend interface (index.html) is missing from app/static.",
        )
    return FileResponse(index_path, media_type="text/html")


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Application Health & Non-Sensitive Configuration",
)
async def health_check():
    """Return application health, registered agents, and local corpus status.

    Does not perform costly model inference. Never exposes API keys.
    """
    settings = get_settings()
    lib_stats = get_library_stats()
    is_groq_ready = settings.is_groq_configured
    library_ready = lib_stats.get("available", False)

    # Status is 'healthy' if basic components are ready; degraded if API key is unconfigured
    health_status = "healthy" if is_groq_ready and library_ready else "degraded"

    return HealthResponse(
        status=health_status,
        app_name=APP_NAME,
        groq_configured=is_groq_ready,
        model=settings.GROQ_MODEL,
        agents=get_agent_names(),
        research_library_available=library_ready,
    )


@app.post(
    "/ask",
    response_model=AskResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Validation Error"},
        503: {"model": ErrorResponse, "description": "Configuration or Service Unavailable"},
        504: {"model": ErrorResponse, "description": "Gateway Timeout"},
        502: {"model": ErrorResponse, "description": "Bad Gateway / Upstream Error"},
    },
    summary="Conduct Multi-Agent Research",
)
async def ask_research_question(req: AskRequest):
    """Receive a user research question, orchestrate the 3-agent team, and return the report."""
    settings = get_settings()

    # Reject request immediately if Groq is not configured
    if not settings.is_groq_configured:
        raise ConfigurationError(
            "Groq API key is not configured. Please set GROQ_API_KEY in your .env file."
        )

    logger.info("Executing research workflow for question: '%s'", req.question[:80])
    result = await run_research_workflow(question=req.question)

    return AskResponse(
        status="success",
        question=req.question,
        answer=result.get("answer", ""),
        sources=result.get("sources", []),
        disclaimer=result.get("disclaimer", EDUCATIONAL_DISCLAIMER),
    )
