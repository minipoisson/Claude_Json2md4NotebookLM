from datetime import datetime, timezone
import convert_claude_history as ch


def test_load_aware_timestamp(tmp_path):
    p = tmp_path / "ts.txt"
    p.write_text("2024-01-15T10:30:00+00:00", encoding="utf-8")
    result = ch.load_last_entry_time(str(p))
    assert result == datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
    assert result.tzinfo is not None # type: ignore


def test_load_naive_timestamp_gets_utc(tmp_path):
    """Naive ISO string must come back as UTC-aware (Bug 4 fix)."""
    p = tmp_path / "ts.txt"
    p.write_text("2024-01-15T10:30:00", encoding="utf-8")
    result = ch.load_last_entry_time(str(p))
    assert result is not None
    assert result.tzinfo is not None
    assert result.tzinfo == timezone.utc
    assert result == datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)


def test_load_invalid_timestamp(tmp_path):
    p = tmp_path / "ts.txt"
    p.write_text("not-a-date", encoding="utf-8")
    assert ch.load_last_entry_time(str(p)) is None


def test_load_missing_file(tmp_path):
    assert ch.load_last_entry_time(str(tmp_path / "nonexistent.txt")) is None


def test_round_trip(tmp_path):
    p = str(tmp_path / "ts.txt")
    dt = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    ch.save_last_entry_time(p, dt)
    result = ch.load_last_entry_time(p)
    assert result == dt


def test_parse_iso_z_suffix():
    dt = ch.parse_iso("2024-01-15T10:30:00Z")
    assert dt.tzinfo is not None
    assert dt == datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)


def test_parse_iso_offset():
    dt = ch.parse_iso("2024-01-15T10:30:00+00:00")
    assert dt.tzinfo is not None


def test_format_timestamp_valid():
    result = ch.format_timestamp("2024-01-15T10:30:00Z")
    assert result == "2024-01-15 10:30:00 UTC"


def test_format_timestamp_empty():
    assert ch.format_timestamp("") == ""


def test_format_timestamp_invalid():
    assert ch.format_timestamp("garbage") == "garbage"
