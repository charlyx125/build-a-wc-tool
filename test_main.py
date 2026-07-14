"""Tests for ccwc.

Run with:  pytest        (or)  python -m pytest
Layer 1 = pure counting functions.  Layer 2 = I/O (read_content) and main().
"""

import io
import os
import sys

import pytest

import main


# --------------------------------------------------------------------------
# Layer 1 — pure counting functions (bytes in, number out)
# --------------------------------------------------------------------------

class TestGetBytes:
    def test_counts_raw_bytes(self):
        assert main.get_bytes(b"hello") == 5

    def test_empty(self):
        assert main.get_bytes(b"") == 0

    def test_multibyte_counts_bytes_not_chars(self):
        # "café" is 4 characters but 5 bytes in UTF-8 (é = 2 bytes)
        assert main.get_bytes("café".encode("utf-8")) == 5


class TestGetChars:
    def test_counts_characters(self):
        assert main.get_chars(b"hello") == 5

    def test_multibyte_counts_chars_not_bytes(self):
        # same "café" — but chars, not bytes, so 4
        assert main.get_chars("café".encode("utf-8")) == 4

    def test_empty(self):
        assert main.get_chars(b"") == 0


class TestGetLines:
    def test_counts_newlines(self):
        assert main.get_lines(b"a\nb\nc\n") == 3

    def test_no_trailing_newline(self):
        # counts \n characters, not "lines" — last partial line has no \n
        assert main.get_lines(b"a\nb\nc") == 2

    def test_empty(self):
        assert main.get_lines(b"") == 0


class TestGetWords:
    def test_counts_words(self):
        assert main.get_words(b"one two three") == 3

    def test_collapses_runs_of_whitespace(self):
        assert main.get_words(b"  lots   of    space  ") == 3

    def test_empty(self):
        assert main.get_words(b"") == 0


# --------------------------------------------------------------------------
# Layer 1 (regression) — CRLF: bytes count \r, lines count only \n
# --------------------------------------------------------------------------

def test_crlf_bytes_include_carriage_returns_but_lines_do_not():
    # The signature bug of this project — Windows CRLF line endings.
    # b"a\r\nb\r\n" is 6 raw bytes and 2 lines.
    data = b"a\r\nb\r\n"
    assert main.get_bytes(data) == 6   # all 6 raw bytes, including both \r
    assert main.get_lines(data) == 2   # 2 newlines (\n) — the \r are not counted
    assert main.get_chars(data) == 6   # 6 characters (each byte is one ASCII char here)


# --------------------------------------------------------------------------
# Layer 2a — read_content (file, missing file, stdin)
# --------------------------------------------------------------------------

def test_read_content_reads_file_as_raw_bytes(tmp_path):
    f = tmp_path / "sample.txt"
    f.write_bytes(b"hello world")
    assert main.read_content([str(f)]) == b"hello world"


def test_read_content_missing_file_exits_with_message(tmp_path, capsys):
    missing = tmp_path / "nope.txt"
    with pytest.raises(SystemExit):
        main.read_content([str(missing)])
    assert "No such file" in capsys.readouterr().out


def test_read_content_reads_stdin_when_no_file(monkeypatch):
    fake_stdin = type("FakeStdin", (), {"buffer": io.BytesIO(b"piped data")})()
    monkeypatch.setattr(sys, "stdin", fake_stdin)
    assert main.read_content([]) == b"piped data"


# --------------------------------------------------------------------------
# Layer 2b — main() end to end (argv in, printed output out)
# --------------------------------------------------------------------------

def run_main(monkeypatch, capsys, argv):
    """Invoke main() as if called with the given command-line args."""
    monkeypatch.setattr(sys, "argv", ["ccwc", *argv])
    main.main()
    return capsys.readouterr().out.strip()


def test_main_byte_flag(tmp_path, monkeypatch, capsys):
    f = tmp_path / "s.txt"
    f.write_bytes(b"hello\nworld\n")  # 12 bytes
    assert run_main(monkeypatch, capsys, ["-c", str(f)]) == "12"


def test_main_default_prints_lines_words_bytes(tmp_path, monkeypatch, capsys):
    f = tmp_path / "s.txt"
    f.write_bytes(b"hello world\nfoo bar\n")  # 2 lines, 4 words, 20 bytes
    assert run_main(monkeypatch, capsys, [str(f)]) == "2 4 20"


@pytest.mark.parametrize(
    "flag, expected",
    [("-l", "1"), ("-w", "1"), ("-c", "6"), ("-m", "5")],
)
def test_main_each_flag_dispatches_correctly(flag, expected, tmp_path, monkeypatch, capsys):
    # "café\n": 1 line, 1 word, 6 bytes, 5 chars — -c and -m deliberately differ
    f = tmp_path / "s.txt"
    f.write_bytes("café\n".encode("utf-8"))
    assert run_main(monkeypatch, capsys, [flag, str(f)]) == expected


def test_main_invalid_flag_reports_error(tmp_path, monkeypatch, capsys):
    f = tmp_path / "s.txt"
    f.write_bytes(b"hello\n")
    assert "invalid option" in run_main(monkeypatch, capsys, ["-x", str(f)])


def test_main_against_challenge_file(monkeypatch, capsys):
    """Regression guard against the real test.txt and its known values."""
    if not os.path.exists("test.txt"):
        pytest.skip("test.txt not present in working directory")
    assert run_main(monkeypatch, capsys, ["test.txt"]) == "7145 58164 342190"
