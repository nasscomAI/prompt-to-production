import argparse
from pathlib import Path

from classifier import batch_classify


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = PROJECT_ROOT / "data" / "city-test-files" / "test_pune.csv"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "results_pune.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify Pune citizen complaints")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input complaints CSV")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output results CSV")
    args = parser.parse_args()

    batch_classify(str(args.input), str(args.output))
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
