#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from pdf2docx import Converter


def convert(pdf_path: Path, docx_path: Path) -> None:
    cv = Converter(str(pdf_path))
    try:
        cv.convert(str(docx_path))
    finally:
        cv.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a text-based PDF to a Word (.docx) file, preserving layout."
    )
    parser.add_argument("pdf", type=Path, help="Path to input PDF file")
    parser.add_argument(
        "-o", "--output", type=Path,
        help="Path to output .docx file (default: same name as input, .docx extension)",
    )
    args = parser.parse_args()

    if not args.pdf.exists():
        sys.exit(f"File not found: {args.pdf}")

    output = args.output or args.pdf.with_suffix(".docx")
    convert(args.pdf, output)
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
