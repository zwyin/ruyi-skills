#!/usr/bin/env python3
"""
scripts/update_changelog.py — keep-a-changelog Unreleased rotation helper

Usage:
    update_changelog.py <changelog_file> <next_version> [--date YYYY-MM-DD]

Behavior:
  1. Rewrites the FIRST `## [Unreleased]` heading line to
     `## [<next_version>] - <date>` (date defaults to today).
  2. Inserts a fresh empty skeleton after the `# Changelog` heading:
         ## [Unreleased]

         ### Added

         ### Fixed
  3. Everything else stays byte-identical (pure line surgery, no YAML).
  4. If no `## [Unreleased]` heading exists: clear error to stderr,
     exit 1, file NOT modified.
"""

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

UNRELEASED = "## [Unreleased]"
CHANGELOG_H1 = "# Changelog"
SKELETON = "## [Unreleased]\n\n### Added\n\n### Fixed\n\n"


def transform(text, next_version, release_date):
    """Return the new file content, or None if no [Unreleased] heading exists."""
    lines = text.splitlines(keepends=True)

    # 1. Locate the FIRST `## [Unreleased]` heading line.
    idx = next((i for i, line in enumerate(lines) if line.strip() == UNRELEASED), None)
    if idx is None:
        return None

    # 2. Rename it in place, preserving the original line ending.
    eol = lines[idx][len(lines[idx].rstrip("\r\n")):] or "\n"
    lines[idx] = "## [{}] - {}{}".format(next_version, release_date, eol)

    # 3. Insert the fresh skeleton after the `# Changelog` heading (skipping
    #    the blank lines that follow it); fall back to just before the
    #    renamed heading if no h1 is present.
    h1 = next((i for i, line in enumerate(lines) if line.strip() == CHANGELOG_H1), None)
    if h1 is not None:
        ins = h1 + 1
        while ins < len(lines) and lines[ins].strip() == "":
            ins += 1
    else:
        ins = idx
    lines[ins:ins] = [SKELETON]

    return "".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Rotate the [Unreleased] section of a keep-a-changelog file."
    )
    parser.add_argument("changelog", help="path to CHANGELOG.md")
    parser.add_argument("next_version", help="version to rename [Unreleased] to, e.g. 0.9.5")
    parser.add_argument(
        "--date",
        dest="release_date",
        default=None,
        help="release date as YYYY-MM-DD (default: today)",
    )
    args = parser.parse_args(argv)

    if args.release_date is not None:
        try:
            # Round-trip check: strptime alone accepts non-padded forms
            # (e.g. "2026-1-1"); require canonical YYYY-MM-DD.
            if datetime.strptime(args.release_date, "%Y-%m-%d").date().isoformat() != args.release_date:
                raise ValueError
        except ValueError:
            print(
                "error: --date must be YYYY-MM-DD, got: {!r}".format(args.release_date),
                file=sys.stderr,
            )
            return 1
    release_date = args.release_date or date.today().isoformat()

    path = Path(args.changelog)
    try:
        # Byte-exact IO: read_bytes/decode + write_bytes/encode avoids
        # universal-newlines translation, so \r\n / \r endings in the
        # untouched parts of the file survive byte-for-byte.
        text = path.read_bytes().decode("utf-8")
    except OSError as exc:
        print("error: cannot read {}: {}".format(path, exc), file=sys.stderr)
        return 1

    new_text = transform(text, args.next_version, release_date)
    if new_text is None:
        print(
            "error: no '{}' section found in {}; nothing to release".format(
                UNRELEASED, path
            ),
            file=sys.stderr,
        )
        return 1

    path.write_bytes(new_text.encode("utf-8"))
    print(
        "Renamed '[Unreleased]' to '[{}] - {}' and inserted a fresh skeleton.".format(
            args.next_version, release_date
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
