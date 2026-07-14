# ccwc

A small clone of the Unix `wc` (word count) tool, built for the
[Coding Challenges `wc` challenge](https://codingchallenges.fyi/challenges/challenge-wc).

Counts bytes, lines, words, and characters from a file or from standard input.

## Install

```
pip install -e .
```

This registers a `ccwc` command. If your shell can't find it afterward, add
Python's user `Scripts` directory to your `PATH`.

## Tests

```
pip install pytest
pytest
```

Covers the counting functions (including CRLF and multibyte edge cases), file /
missing-file / stdin reading, and each flag end-to-end.

## Usage

```
ccwc -c <file>      # bytes
ccwc -l <file>      # lines
ccwc -w <file>      # words
ccwc -m <file>      # characters (multibyte-aware)
ccwc <file>         # default: lines words bytes
cat <file> | ccwc   # read from standard input instead of a file
```

## Notes

- **Bytes are counted from the raw file** (opened in binary mode), so the count
  matches `wc -c` even when the file uses `CRLF` line endings or non-ASCII
  characters. Lines and words are counted on the UTF-8–decoded text.
  - *CRLF* — Windows ends each line with two bytes (`\r\n`) where Unix uses one
    (`\n`). Reading as text silently drops the `\r`, undercounting bytes; binary
    mode keeps them.
  - *Non-ASCII* — characters beyond basic English (e.g. `é`, `—`, curly quotes)
    take 2–4 bytes each in UTF-8, so byte count ≠ character count. `wc -c` counts
    bytes; `wc -m` counts characters.
- **PowerShell pipes can change the byte count.** On Windows, `cat file | ccwc -c`
  may report fewer bytes than `ccwc -c file`. PowerShell pipes carry *text*, not
  raw bytes, so it re-encodes the stream in transit. This is a shell behavior, not
  a bug in `ccwc` — reading the file directly, or piping from Bash/WSL, gives the
  correct count.
