"""
City complaint summary — per-ward days_open statistics for citizen complaint data.

Separate tool from app.py (which stays budget-only). Operates per (city, ward);
it never aggregates across cities or wards, and refuses input that lacks the
expected complaint schema.
"""
import argparse
import csv
import glob
import os
import sys

REQUIRED_COLUMNS = [
    "complaint_id",
    "date_raised",
    "city",
    "ward",
    "location",
    "description",
    "reported_by",
    "days_open",
]

OUTPUT_COLUMNS = [
    "city",
    "ward",
    "complaint_count",
    "days_open_min",
    "days_open_avg",
    "days_open_max",
]


def load_complaints(path):
    """Reads a complaint CSV, validates schema, returns rows."""
    if not os.path.exists(path):
        raise FileNotFoundError("input file not found: {0}".format(path))
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError("input file has no data rows: {0}".format(path))
    missing = [c for c in REQUIRED_COLUMNS if c not in rows[0]]
    if missing:
        raise ValueError(
            "input file missing required columns: {0}".format(", ".join(missing))
        )
    return rows


def summarize_ward(rows):
    """Per-ward days_open statistics for one city's complaint rows."""
    wards = sorted({r["ward"] for r in rows})
    output = []
    for ward in wards:
        days = [float(r["days_open"]) for r in rows if r["ward"] == ward]
        output.append({
            "city": rows[0]["city"],
            "ward": ward,
            "complaint_count": len(days),
            "days_open_min": round(min(days), 1),
            "days_open_avg": round(sum(days) / len(days), 2),
            "days_open_max": round(max(days), 1),
        })
    return output


def write_output(path, output_rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(output_rows)


def main():
    parser = argparse.ArgumentParser(
        description="Per-ward days_open summary for citizen complaint CSVs"
    )
    parser.add_argument(
        "--dir",
        default=os.path.join("..", "data", "city-test-files"),
        help="Directory containing test_*.csv files to process",
    )
    parser.add_argument("--input", help="Single input file (overrides --dir)")
    parser.add_argument(
        "--output", help="Single output file (requires --input)"
    )
    args = parser.parse_args()

    if args.input:
        if not args.output:
            sys.exit("REFUSE: --output is required when --input is given.")
        try:
            rows = load_complaints(args.input)
        except (FileNotFoundError, ValueError) as exc:
            sys.exit("REFUSE: {0}".format(exc))
        result = summarize_ward(rows)
        write_output(args.output, result)
        print("Wrote {0} wards from {1} to {2}".format(
            len(result), os.path.basename(args.input), args.output
        ))
        return

    if not os.path.isdir(args.dir):
        sys.exit("REFUSE: directory not found: {0}".format(args.dir))
    inputs = sorted(glob.glob(os.path.join(args.dir, "test_*.csv")))
    if not inputs:
        sys.exit("REFUSE: no test_*.csv files found in {0}".format(args.dir))

    for path in inputs:
        try:
            rows = load_complaints(path)
        except (FileNotFoundError, ValueError) as exc:
            sys.exit("REFUSE: {0}".format(exc))
        city = os.path.basename(path)[len("test_"):-len(".csv")]
        result = summarize_ward(rows)
        output_path = "result_{0}.csv".format(city)
        write_output(output_path, result)
        print("Wrote {0} wards from {1} to {2}".format(
            len(result), os.path.basename(path), output_path
        ))


if __name__ == "__main__":
    main()
