from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class LogEntry(BaseModel):
    timestamp: datetime
    level: LogLevel
    source: str = Field(min_length=1)
    message: str = Field(min_length=1)
    line_number: int = Field(ge=1)

    @field_validator("level", mode="before")
    @classmethod
    def normalize_level(cls, value: str) -> str:
        # Permite logs com "error", "Error" etc., mas guarda tudo padronizado.
        return str(value).upper()


class AnalysisReport(BaseModel):
    total: int
    by_level: dict[str, int]
    by_source: dict[str, int]
    top_messages: list[tuple[str, int]]
    first_timestamp: datetime | None
    last_timestamp: datetime | None
    invalid_lines: list[str]
