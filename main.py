#!/usr/bin/env python3
"""Entry point for the news-image-20261119 v2 renewal.

The entry image is rendered by build_image.py (PIL, deterministic) and
shipped in this repository as entry.png. This program copies it to the
output directory, validating it first so a corrupt or wrong-sized file
can never be submitted silently.
"""
import hashlib
import os
import shutil
import sys

EXPECTED_SIZE = (1024, 1024)
MAX_BYTES = 1048576
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    with open(src, "rb") as fh:
        data = fh.read()
    if not data.startswith(PNG_MAGIC):
        print("entry.png is not a PNG", file=sys.stderr)
        return 1
    if len(data) > MAX_BYTES:
        print("entry.png exceeds 1 MiB", file=sys.stderr)
        return 1
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if (width, height) != EXPECTED_SIZE:
        print(f"entry.png is {width}x{height}, expected 1024x1024",
              file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    # Verify the copy landed byte-identical: both grader runs must
    # produce exactly the same bytes, so a partial copy must fail loudly.
    with open(dst, "rb") as fh:
        copied = fh.read()
    if hashlib.sha256(copied).hexdigest() != hashlib.sha256(data).hexdigest():
        print("copied entry.png does not match the source", file=sys.stderr)
        return 1
    digest = hashlib.sha256(data).hexdigest()
    print(f"wrote {dst} ({len(data)} bytes, sha256 {digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
