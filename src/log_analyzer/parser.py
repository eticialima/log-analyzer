import re
from collections import Counter
from datetime import timezone
from pathlib import Path

from dateutil import parser as date_parser
from pydantic import ValidationError

from log_analyzer.models import AnalysisReport, LogEntry


LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\S+(?:\s+\S+)?)\s+"
    r"(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL|debug|info|warning|error|critical)\s+"
    r"(?P<source>[\w.-]+)\s+"
    r"(?P<message>.+)$"
)


def parse_line(line: str, line_number: int) -> LogEntry:
    match = LOG_PATTERN.match(line.strip())
    if not match:
        raise ValueError("line does not match expected format")

    data = match.groupdict()
    data["timestamp"] = normalize_timestamp(date_parser.parse(data["timestamp"]))
    data["line_number"] = line_number
    return LogEntry(**data)


def normalize_timestamp(value):
    # Logs misturam datas com timezone e sem timezone. Normalizar evita erro ao comparar.
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def parse_file(path: Path) -> tuple[list[LogEntry], list[str]]:
    entries: list[LogEntry] = []
    invalid_lines: list[str] = []

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue

        try:
            entries.append(parse_line(line, line_number))
        except (ValueError, ValidationError) as error:
            invalid_lines.append(f"line {line_number}: {line} ({error})")

    return entries, invalid_lines


def analyze_entries(entries: list[LogEntry], invalid_lines: list[str]) -> AnalysisReport:
    by_level = Counter(entry.level for entry in entries)
    by_source = Counter(entry.source for entry in entries)
    by_message = Counter(entry.message for entry in entries)
    timestamps = [entry.timestamp for entry in entries]

    return AnalysisReport(
        total=len(entries),
        by_level=dict(by_level),
        by_source=dict(by_source),
        top_messages=by_message.most_common(5),
        first_timestamp=min(timestamps) if timestamps else None,
        last_timestamp=max(timestamps) if timestamps else None,
        invalid_lines=invalid_lines,
    )


def analyze_file(path: Path, level: str | None = None) -> AnalysisReport:
    entries, invalid_lines = parse_file(path)

    if level:
        entries = [entry for entry in entries if entry.level == level.upper()]

    return analyze_entries(entries, invalid_lines)
