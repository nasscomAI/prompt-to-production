"""
UC-0B app.py — Policy summarization CLI.

Usage:
    python app.py --input <policy.txt> --output <output.txt>
"""
import argparse
import logging
import sys
from pathlib import Path

from classifier import retrieve_policy, summarize_policy

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize a policy document preserving every clause."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the .txt policy document",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write the summary output",
    )
    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        output_path = Path(args.output)
        output_path.write_text(summary, encoding="utf-8")
        logger.info("Summary written to %s", output_path.resolve())
    except (FileNotFoundError, ValueError) as e:
        logger.error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
