"""Command-line entry point for csvdiff-cli."""

import sys
import argparse

from csvdiff.parser import load_csv, CSVParseError
from csvdiff.differ import diff_csvs
from csvdiff.formatter import format_diff


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csvdiff",
        description="Compare two CSV files with column-level granularity.",
    )
    parser.add_argument("file_a", help="Baseline CSV file")
    parser.add_argument("file_b", help="Changed CSV file")
    parser.add_argument(
        "--key", "-k",
        metavar="COLUMN",
        default=None,
        help="Column to use as row identifier (default: first column)",
    )
    parser.add_argument(
        "--delimiter", "-d",
        default=",",
        help="CSV delimiter character (default: ',')",
    )
    parser.add_argument(
        "--encoding", "-e",
        default="utf-8",
        help="File encoding (default: utf-8)",
    )
    parser.add_argument(
        "--ignore", "-i",
        metavar="COLUMN",
        action="append",
        default=[],
        help="Column(s) to ignore (can be repeated)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        parsed_a = load_csv(args.file_a, delimiter=args.delimiter,
                            encoding=args.encoding, key_column=args.key)
        parsed_b = load_csv(args.file_b, delimiter=args.delimiter,
                            encoding=args.encoding, key_column=args.key)
    except CSVParseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    result = diff_csvs(parsed_a, parsed_b, ignore_columns=args.ignore)
    output = format_diff(result, use_color=not args.no_color)
    print(output)

    return 0 if not result.has_changes else 1


if __name__ == "__main__":
    sys.exit(main())
