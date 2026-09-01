import csv
import json
from pathlib import Path

from log_analyzer.models import AnalysisReport


def export_json(report: AnalysisReport, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report.model_dump_json(indent=2), encoding="utf-8")


def export_csv(report: AnalysisReport, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["section", "name", "count"])

        for level, count in report.by_level.items():
            writer.writerow(["level", level, count])

        for source, count in report.by_source.items():
            writer.writerow(["source", source, count])

        for message, count in report.top_messages:
            writer.writerow(["message", message, count])
