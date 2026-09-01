# Log Analyzer

A small Python CLI for analyzing application logs.

It uses:

- `Typer` for CLI commands
- `Rich` for terminal tables and panels
- `Pydantic` for validating parsed log entries
- `Loguru` for internal tool logs
- `python-dateutil` for parsing timestamps
- `pytest` for tests

## Install

```bash
cd log-analyzer
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Generate A Sample Log

```bash
log-analyzer sample sample.log
```

## Analyze

```bash
log-analyzer analyze sample.log
log-analyzer analyze sample.log --level ERROR
```

## Export

```bash
log-analyzer export sample.log --format json --output reports/report.json
log-analyzer export sample.log --format csv --output reports/report.csv
```

## Run Tests

```bash
pytest
```

## Supported Log Format

```txt
2026-09-01 10:00:01 INFO api User logged in
2026-09-01T10:00:02Z ERROR worker Job failed
```

The parser expects:

```txt
timestamp level source message
```
