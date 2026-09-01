from pathlib import Path

from log_analyzer.parser import analyze_file, parse_line


def test_parse_line_accepts_basic_log() -> None:
    entry = parse_line("2026-09-01 10:00:01 info api User logged in", 1)

    assert entry.level == "INFO"
    assert entry.source == "api"
    assert entry.message == "User logged in"
    assert entry.line_number == 1


def test_analyze_file_counts_levels(tmp_path: Path) -> None:
    log_file = tmp_path / "app.log"
    log_file.write_text(
        "\n".join(
            [
                "2026-09-01 10:00:01 INFO api User logged in",
                "2026-09-01 10:00:02 ERROR worker Job failed",
                "bad line",
                "2026-09-01 10:00:03 ERROR worker Job failed",
            ]
        ),
        encoding="utf-8",
    )

    report = analyze_file(log_file)

    assert report.total == 3
    assert report.by_level["INFO"] == 1
    assert report.by_level["ERROR"] == 2
    assert report.top_messages[0] == ("Job failed", 2)
    assert len(report.invalid_lines) == 1


def test_analyze_file_handles_mixed_timezones(tmp_path: Path) -> None:
    log_file = tmp_path / "mixed-timezones.log"
    log_file.write_text(
        "\n".join(
            [
                "2026-09-01 10:00:01 INFO api Without timezone",
                "2026-09-01T10:00:02Z ERROR worker With timezone",
            ]
        ),
        encoding="utf-8",
    )

    report = analyze_file(log_file)

    assert report.total == 2
    assert report.first_timestamp is not None
    assert report.last_timestamp is not None
