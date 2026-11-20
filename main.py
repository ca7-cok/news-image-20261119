#!/usr/bin/env python3
"""Entry point: copy the pre-rendered entry.png beside this file to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png when set).
Standard library only; deterministic: the same bytes every run."""

import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print("wrote", dst)


if __name__ == "__main__":
    sys.exit(main())
