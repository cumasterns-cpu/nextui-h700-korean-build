#!/usr/bin/env python3
"""Validate a NextUI .lang translation against the PR #735 en.lang reference."""
from __future__ import annotations
import re
import sys
from collections import Counter
from pathlib import Path

PLACEHOLDER = re.compile(r"%(?:[-+ #0']*)?(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|z|j|t|L)?[diuoxXfFeEgGaAcspn%]")

def parse(path: Path):
    entries = {}
    duplicates = []
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.lstrip(" \t")
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.rstrip(" \t")
        value = value.lstrip(" \t").rstrip(" \t\r")
        if key in entries:
            duplicates.append((n, key))
        entries[key] = value
    return entries, duplicates

def main():
    if len(sys.argv) != 3:
        print("Usage: validate_ko_lang.py en.lang ko.lang")
        return 2
    en_path, ko_path = map(Path, sys.argv[1:])
    en, en_dups = parse(en_path)
    ko, ko_dups = parse(ko_path)
    missing = sorted(set(en) - set(ko))
    extra = sorted(set(ko) - set(en))
    fmt = []
    for key in sorted(set(en) & set(ko)):
        a = Counter(PLACEHOLDER.findall(en[key]))
        b = Counter(PLACEHOLDER.findall(ko[key]))
        if a != b:
            fmt.append((key, sorted(a.items()), sorted(b.items())))
    long_lines = [(n, len(line.encode("utf-8"))) for n, line in enumerate(ko_path.read_text(encoding="utf-8").splitlines(), 1) if len(line.encode("utf-8")) >= 1024]
    print(f"en.lang entries: {len(en)}")
    print(f"ko.lang entries: {len(ko)}")
    print(f"Missing keys: {len(missing)}")
    print(f"Extra keys: {len(extra)}")
    print(f"Placeholder mismatches: {len(fmt)}")
    print(f"Duplicate keys: {len(en_dups) + len(ko_dups)}")
    print(f"Lines >= 1024 bytes: {len(long_lines)}")
    for title, values in (("MISSING", missing), ("EXTRA", extra)):
        for value in values[:80]: print(f"{title}: {value}")
    for key, a, b in fmt: print(f"FORMAT: {key}: en={a}, ko={b}")
    for item in en_dups + ko_dups: print(f"DUPLICATE: line {item[0]} key={item[1]}")
    for item in long_lines: print(f"LONG LINE: line {item[0]} bytes={item[1]}")
    return 1 if (missing or extra or fmt or en_dups or ko_dups or long_lines) else 0

if __name__ == "__main__":
    raise SystemExit(main())
