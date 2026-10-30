"""Configuration management for ResearchBot.

Loads environment variables, validates settings, and ensures sensitive credentials
are kept safe from logs and API responses.
"""

from functools import lru_cache
import os
from typing import List
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load local .env if present
load_dotenv(override=False)

APP_NAME = "ResearchBot — Multi-Agent Research & Analysis Assistant"

AGENT_NAMES: List[str] = [
    "Research Query Analyzer",
    "Research & Analysis Agent",
    "Research Answer Reviewer",
]

EDUCATIONAL_DISCLAIMER: str = (
    "Disclaimer: ResearchBot is an educational research and analysis assistant "
    "designed for learning and demonstration. Its output may contain mistakes, "
    "incomplete information, or outdated findings. Results are limited by the sources "
    "available to the system and do not replace independent verification, professional "
    "judgment, or consultation with qualified experts where appropriate."
)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    GROQ_API_KEY: str = Field(default="", validation_alias="GROQ_API_KEY")
    GROQ_MODEL: str = Field(default="llama-3.3-70b-versatile", validation_alias="GROQ_MODEL")
    HOST: str = Field(default="127.0.0.1", validation_alias="HOST")
    PORT: int = Field(default=8000, validation_alias="PORT")
    REQUEST_TIMEOUT: int = Field(default=60, validation_alias="REQUEST_TIMEOUT")
    MAX_QUESTION_LENGTH: int = Field(default=5000, validation_alias="MAX_QUESTION_LENGTH")
    MAX_RESEARCH_RESULTS: int = Field(default=5, validation_alias="MAX_RESEARCH_RESULTS")

    @property
    def is_groq_configured(self) -> bool:
        """Check if Groq API key is present and non-placeholder."""
        key = self.GROQ_API_KEY.strip() if self.GROQ_API_KEY else ""
        if not key:
            return False
        # Guard against placeholder values
        placeholders = {"your_actual_groq_api_key", "your_groq_api_key", "none", "null", "placeholder"}
        return key.lower() not in placeholders

    def get_safe_dict(self) -> dict:
        """Return non-sensitive configuration parameters for logging and monitoring."""
        return {
            "app_name": APP_NAME,
            "groq_configured": self.is_groq_configured,
            "groq_model": self.GROQ_MODEL,
            "host": self.HOST,
            "port": self.PORT,
            "request_timeout": self.REQUEST_TIMEOUT,
            "max_question_length": self.MAX_QUESTION_LENGTH,
            "max_research_results": self.MAX_RESEARCH_RESULTS,
        }


def get_settings() -> Settings:
    """Return Settings instance populated from environment variables and .env."""
    return Settings()


# Compatibility for test harnesses that call cache_clear
get_settings.cache_clear = lambda: None
