from pathlib import Path
from typing import Literal

import typer
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from log_analyzer.exporters import export_csv, export_json
from log_analyzer.parser import analyze_file


app = typer.Typer(help="Analyze application logs from the terminal.", no_args_is_help=True)
console = Console()
logger.remove()


def ensure_log_file(path: Path) -> None:
    if not path.exists():
        console.print(f"[red]Log file not found:[/red] {path}")
        raise typer.Exit(code=1)

    if not path.is_file():
        console.print(f"[red]Path is not a file:[/red] {path}")
        raise typer.Exit(code=1)


def print_report(report) -> None:
    console.print(
        Panel.fit(
            f"Valid lines: [bold]{report.total}[/bold]\n"
            f"Invalid lines: [bold]{len(report.invalid_lines)}[/bold]\n"
            f"Range: {report.first_timestamp or '-'} -> {report.last_timestamp or '-'}",
            title="Summary",
        )
    )

    level_table = Table(title="By Level")
    level_table.add_column("Level")
    level_table.add_column("Count", justify="right")
    for level, count in sorted(report.by_level.items()):
        style = "red" if level in {"ERROR", "CRITICAL"} else "green"
        level_table.add_row(f"[{style}]{level}[/{style}]", str(count))
    console.print(level_table)

    source_table = Table(title="By Source")
    source_table.add_column("Source")
    source_table.add_column("Count", justify="right")
    for source, count in sorted(report.by_source.items(), key=lambda item: item[1], reverse=True):
        source_table.add_row(source, str(count))
    console.print(source_table)

    message_table = Table(title="Top Messages")
    message_table.add_column("Message")
    message_table.add_column("Count", justify="right")
    for message, count in report.top_messages:
        message_table.add_row(message, str(count))
    console.print(message_table)

    if report.invalid_lines:
        console.print("[yellow]Some lines could not be parsed. Use the original log to inspect them.[/yellow]")


@app.callback()
def configure(debug: bool = typer.Option(False, "--debug", help="Show internal tool logs.")) -> None:
    if debug:
        logger.add(lambda message: console.print(f"[dim]{message}[/dim]"))


@app.command()
def analyze(
    path: Path = typer.Argument(..., help="Log file to analyze."),
    level: str | None = typer.Option(None, "--level", "-l", help="Filter by level, like ERROR or INFO."),
) -> None:
    """Analyze a log file and print a terminal report."""
    ensure_log_file(path)
    logger.info("Analyzing {}", path)
    report = analyze_file(path, level=level)
    print_report(report)


@app.command()
def export(
    path: Path = typer.Argument(..., help="Log file to analyze."),
    format: Literal["json", "csv"] = typer.Option("json", "--format", "-f", help="Export format."),
    output: Path = typer.Option(Path("reports/report.json"), "--output", "-o", help="Output file."),
    level: str | None = typer.Option(None, "--level", "-l", help="Filter by level, like ERROR or INFO."),
) -> None:
    """Analyze a log file and export the report."""
    ensure_log_file(path)
    logger.info("Exporting {} report from {}", format, path)
    report = analyze_file(path, level=level)

    if format == "json":
        export_json(report, output)
    else:
        export_csv(report, output)

    console.print(f"[green]Report exported:[/green] {output}")


@app.command()
def sample(output: Path = typer.Argument(Path("sample.log"), help="Where to write the sample log.")) -> None:
    """Create a sample log file for testing."""
    output.write_text(
        "\n".join(
            [
                "2026-09-01 10:00:01 INFO api User logged in",
                "2026-09-01 10:00:05 ERROR worker Job failed",
                "2026-09-01 10:00:08 WARNING api Slow request",
                "2026-09-01 10:00:10 ERROR worker Job failed",
                "2026-09-01T10:00:12Z CRITICAL db Connection lost",
                "this is not a valid log line",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    console.print(f"[green]Sample log written:[/green] {output}")


if __name__ == "__main__":
    app()
