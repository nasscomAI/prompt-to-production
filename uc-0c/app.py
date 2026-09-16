import argparse
import csv
import sys
from pathlib import Path


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def load_dataset(path):
    """Load and validate the CSV, reporting all null actual_spend rows."""
    try:
        with Path(path).open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ValueError("CSV has no header row")
            missing = REQUIRED_COLUMNS - set(reader.fieldnames)
            if missing:
                raise ValueError(f"missing required columns: {', '.join(sorted(missing))}")
            rows = list(reader)
    except (OSError, csv.Error) as exc:
        raise ValueError(f"could not read CSV: {exc}") from exc

    null_rows = []
    for number, row in enumerate(rows, start=2):
        try:
            float(row["budgeted_amount"])
            if row["actual_spend"].strip() == "":
                null_rows.append((number, row))
            else:
                float(row["actual_spend"])
        except (AttributeError, ValueError) as exc:
            raise ValueError(f"invalid numeric value on CSV line {number}: {exc}") from exc

    print(f"Loaded {len(rows)} rows; null actual_spend: {len(null_rows)}", file=sys.stderr)
    for number, row in null_rows:
        print(
            f"NULL line {number}: {row['period']} | {row['ward']} | "
            f"{row['category']} | reason: {row['notes']}",
            file=sys.stderr,
        )
    return rows


def compute_growth(rows, ward, category, growth_type):
    """Return a per-period growth table for one exact ward/category pair."""
    growth_type = growth_type.upper()
    if growth_type not in {"MOM", "YOY"}:
        raise ValueError("growth_type must be MoM or YoY")
    selected = [row for row in rows if row["ward"] == ward and row["category"] == category]
    if not selected:
        raise ValueError(f"no rows found for ward={ward!r}, category={category!r}")
    selected.sort(key=lambda row: row["period"])

    result = []
    for index, row in enumerate(selected):
        current_text = row["actual_spend"].strip()
        base_index = index - 1 if growth_type == "MOM" else index - 12
        output = {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": current_text or "NULL",
            "growth_type": growth_type,
            "growth": "",
            "formula": "",
            "status": "computed",
            "null_reason": "",
        }
        if not current_text:
            output["status"] = "flagged_null_actual_spend"
            output["null_reason"] = row["notes"]
        elif base_index < 0 or not selected[base_index]["actual_spend"].strip():
            output["status"] = "not_computed_missing_comparison"
            output["formula"] = "growth = (current - comparison) / comparison * 100"
        else:
            current = float(current_text)
            comparison = float(selected[base_index]["actual_spend"])
            if comparison == 0:
                output["status"] = "not_computed_zero_comparison"
                output["formula"] = "growth = (current - comparison) / comparison * 100"
            else:
                growth = (current - comparison) / comparison * 100
                comparison_period = selected[base_index]["period"]
                output["growth"] = f"{growth:.1f}%"
                output["formula"] = (
                    f"({current_text} - {comparison:g}) / {comparison:g} * 100 = "
                    f"{growth:.1f}% ({row['period']} vs {comparison_period})"
                )
        result.append(output)
    return result


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="input budget CSV")
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"])
    parser.add_argument("--output", required=True, help="output CSV path")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.ward.strip().lower() in {"any", "all", "all wards"} or args.category.strip().lower() in {
        "any", "all", "all categories"
    }:
        raise ValueError("refusing all-ward or all-category aggregation")
    rows = load_dataset(args.input)
    result = compute_growth(rows, args.ward, args.category, args.growth_type)
    output_path = Path(args.output)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=result[0].keys())
        writer.writeheader()
        writer.writerows(result)
    print(f"Wrote {len(result)} rows to {output_path}")


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(2)
