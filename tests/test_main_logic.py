import json
import os
from unittest.mock import patch
import convert_claude_history as ch


def _make_conv(uid, name, updated):
    return {
        "uuid": uid,
        "name": name,
        "created_at": updated,
        "updated_at": updated,
        "chat_messages": [
            {"sender": "human", "text": "Hello", "created_at": updated},
            {"sender": "assistant", "text": "Hi there", "created_at": updated},
        ],
    }


def _write_json(convs, tmp_path, filename="convs.json"):
    p = tmp_path / filename
    p.write_text(json.dumps(convs), encoding="utf-8")
    return str(p)


def _run(tmp_path, convs, limit=10_000_000, input_filename="convs.json"):
    input_file = _write_json(convs, tmp_path, input_filename)
    output_file = str(tmp_path / "Out.md")
    ts_file = str(tmp_path / "last_entry_time.txt")

    with patch("sys.argv", ["prog", "--input_file", input_file,
                             "--output_file", output_file,
                             "--limit", str(limit)]), \
         patch("convert_claude_history.LAST_ENTRY_FILE", ts_file):
        ch.main()

    return output_file, ts_file


def _content(out_file, index=1):
    return open(ch.generate_output_path(out_file, index), encoding="utf-8").read()


# --- basic run ---

def test_fresh_run_creates_01(tmp_path):
    convs = [_make_conv("a", "Conv A", "2024-01-01T00:00:00Z")]
    out_file, _ = _run(tmp_path, convs)
    assert os.path.exists(ch.generate_output_path(out_file, 1))
    assert "Conv A" in _content(out_file, 1)


def test_fresh_run_saves_timestamp(tmp_path):
    convs = [_make_conv("a", "Conv A", "2024-01-01T00:00:00Z")]
    _, ts_file = _run(tmp_path, convs)
    assert os.path.exists(ts_file)
    dt = ch.load_last_entry_time(ts_file)
    assert dt is not None
    assert dt.tzinfo is not None


# --- incremental ---

def test_incremental_skips_old_conversations(tmp_path):
    convs = [_make_conv("a", "Conv A", "2024-01-01T00:00:00Z")]
    out_file, ts_file = _run(tmp_path, convs)

    convs2_file = _write_json(convs, tmp_path, "convs2.json")
    with patch("sys.argv", ["prog", "--input_file", convs2_file,
                             "--output_file", out_file, "--limit", "10000000"]), \
         patch("convert_claude_history.LAST_ENTRY_FILE", ts_file), \
         patch("builtins.print") as mock_print:
        ch.main()

    calls = " ".join(str(c) for c in mock_print.call_args_list)
    assert "0" in calls


def test_second_run_appends_new_only(tmp_path):
    convs1 = [_make_conv("a", "Conv A", "2024-01-01T00:00:00Z")]
    out_file, ts_file = _run(tmp_path, convs1)

    convs2 = convs1 + [_make_conv("b", "Conv B", "2024-01-02T00:00:00Z")]
    convs2_file = _write_json(convs2, tmp_path, "convs2.json")
    with patch("sys.argv", ["prog", "--input_file", convs2_file,
                             "--output_file", out_file, "--limit", "10000000"]), \
         patch("convert_claude_history.LAST_ENTRY_FILE", ts_file):
        ch.main()

    content = _content(out_file, 1)
    assert content.count("Conv A") == 1
    assert content.count("Conv B") == 1


# --- file size limit ---

def test_size_limit_splits_into_two_files(tmp_path):
    convs = [
        _make_conv("a", "Conv A", "2024-01-01T00:00:00Z"),
        _make_conv("b", "Conv B", "2024-01-02T00:00:00Z"),
    ]
    out_file, _ = _run(tmp_path, convs, limit=300)
    assert os.path.exists(ch.generate_output_path(out_file, 1))
    assert os.path.exists(ch.generate_output_path(out_file, 2))


# --- state desync (Bug 2 fix) ---

def test_state_desync_missing_timestamp_no_duplication(tmp_path):
    """Output exists but no timestamp → fresh write, no duplicates."""
    convs = [_make_conv("a", "Conv A", "2024-01-01T00:00:00Z")]
    out_file, ts_file = _run(tmp_path, convs)

    os.remove(ts_file)

    convs_file = _write_json(convs, tmp_path, "convs2.json")
    with patch("sys.argv", ["prog", "--input_file", convs_file,
                             "--output_file", out_file, "--limit", "10000000"]), \
         patch("convert_claude_history.LAST_ENTRY_FILE", ts_file):
        ch.main()

    content = _content(out_file, 1)
    assert content.count("Conv A") == 1


# --- non-contiguous gap (Bug 3 fix) ---

def test_non_contiguous_gap_targets_highest_file(tmp_path):
    """-01.md and -03.md exist (gap at -02.md) → new content appended to -03.md."""
    convs1 = [_make_conv("a", "Conv A", "2024-01-01T00:00:00Z")]
    out_file, ts_file = _run(tmp_path, convs1)

    p03 = ch.generate_output_path(out_file, 3)
    with open(p03, "w", encoding="utf-8") as f:
        f.write("# Existing\n")

    convs2 = convs1 + [_make_conv("b", "Conv B", "2024-01-02T00:00:00Z")]
    convs2_file = _write_json(convs2, tmp_path, "convs2.json")
    with patch("sys.argv", ["prog", "--input_file", convs2_file,
                             "--output_file", out_file, "--limit", "10000000"]), \
         patch("convert_claude_history.LAST_ENTRY_FILE", ts_file):
        ch.main()

    assert "Conv B" in open(p03, encoding="utf-8").read()


# --- naive timestamp (Bug 4 fix) ---

def test_naive_timestamp_file_no_crash(tmp_path):
    """Naive ISO string in last_entry_time.txt must not raise TypeError."""
    convs = [_make_conv("a", "Conv A", "2024-01-01T00:00:00Z")]
    out_file, ts_file = _run(tmp_path, convs)

    with open(ts_file, "w", encoding="utf-8") as f:
        f.write("2024-01-01T00:00:00")

    convs2 = convs + [_make_conv("b", "Conv B", "2024-01-02T00:00:00Z")]
    convs2_file = _write_json(convs2, tmp_path, "convs2.json")
    with patch("sys.argv", ["prog", "--input_file", convs2_file,
                             "--output_file", out_file, "--limit", "10000000"]), \
         patch("convert_claude_history.LAST_ENTRY_FILE", ts_file):
        ch.main()

    assert "Conv B" in _content(out_file, 1)


# --- conversations without updated_at ---

def test_conv_without_updated_at_not_skipped(tmp_path):
    conv = {
        "uuid": "x",
        "name": "No Date",
        "created_at": "",
        "updated_at": "",
        "chat_messages": [{"sender": "human", "text": "Hello", "created_at": ""}],
    }
    out_file, ts_file = _run(tmp_path, [conv])
    assert os.path.exists(ch.generate_output_path(out_file, 1))
    assert "No Date" in _content(out_file, 1)


def test_conv_without_updated_at_no_timestamp_saved(tmp_path):
    conv = {
        "uuid": "x",
        "name": "No Date",
        "created_at": "",
        "updated_at": "",
        "chat_messages": [{"sender": "human", "text": "Hello", "created_at": ""}],
    }
    _, ts_file = _run(tmp_path, [conv])
    assert not os.path.exists(ts_file)
