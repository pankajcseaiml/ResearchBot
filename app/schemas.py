"""Pydantic schemas for request and response validation in ResearchBot."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from app.config import AGENT_NAMES, APP_NAME, EDUCATIONAL_DISCLAIMER, get_settings


class AskRequest(BaseModel):
    """Incoming user research question."""

    question: str = Field(
        ...,
        description="The research question to be investigated by the multi-agent team.",
        examples=["What are the benefits, limitations, and practical applications of Retrieval-Augmented Generation in AI systems?"],
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        """Validate question length and presence of meaningful content."""
        if not isinstance(v, str):
            raise ValueError("Question must be a valid text string.")
        
        normalized = v.strip()
        if not normalized:
            raise ValueError("Question cannot be empty or contain only whitespace.")
        
        settings = get_settings()
        if len(normalized) > settings.MAX_QUESTION_LENGTH:
            raise ValueError(
                f"Question exceeds maximum permitted length of {settings.MAX_QUESTION_LENGTH} characters."
            )
        
        return normalized


class AskResponse(BaseModel):
    """Structured response returned after multi-agent research analysis."""

    status: str = Field(default="success", description="Status indicator for the operation.")
    question: str = Field(..., description="The original normalized research question.")
    answer: str = Field(..., description="Synthesized Markdown research report from the reviewer agent.")
    sources: List[str] = Field(
        default_factory=list,
        description="Curated sources and document identifiers consulted during research.",
    )
    disclaimer: str = Field(
        default=EDUCATIONAL_DISCLAIMER,
        description="Mandatory educational disclaimer.",
    )


class HealthResponse(BaseModel):
    """System health and non-sensitive configuration status."""

    status: str = Field(..., description="Overall health indicator: 'healthy' or 'degraded'.")
    app_name: str = Field(default=APP_NAME, description="Application display name.")
    groq_configured: bool = Field(..., description="Whether the Groq API key is configured.")
    model: str = Field(..., description="Active language model identifier.")
    agents: List[str] = Field(
        default_factory=lambda: list(AGENT_NAMES),
        description="Names of registered coordinating research agents.",
    )
    research_library_available: bool = Field(
        ..., description="Whether local curated research documents are loaded and available."
    )


class ErrorResponse(BaseModel):
    """Consistent error payload for client and API issues."""

    status: str = Field(default="error", description="Error status indicator.")
    message: str = Field(..., description="Human-readable explanation of the error.")
    detail: Optional[str] = Field(default=None, description="Safe additional error context if available.")
