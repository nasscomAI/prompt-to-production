import argparse
import csv
import re
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


def _match_key(value):
    """Normalize punctuation/encoding variants for identifiers such as ward names."""
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def load_dataset(input_path):
    """Load and validate the CSV, reporting all null actual_spend rows."""
    path = Path(input_path)
    if not path.is_file():
        raise ValueError(f"Input file not found: {input_path}")

    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header row")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))

        rows = []
        null_rows = []
        for row_number, row in enumerate(reader, start=2):
            if not row.get("period") or not row.get("ward") or not row.get("category"):
                raise ValueError(f"Missing identifying value on CSV row {row_number}")
            try:
                row["budgeted_amount"] = float(row["budgeted_amount"])
            except (TypeError, ValueError):
                raise ValueError(f"Invalid budgeted_amount on CSV row {row_number}")

            actual = (row.get("actual_spend") or "").strip()
            if actual == "":
                row["actual_spend"] = None
                null_rows.append(row)
            else:
                try:
                    row["actual_spend"] = float(actual)
                except ValueError:
                    raise ValueError(f"Invalid actual_spend on CSV row {row_number}")
            rows.append(row)

    print(f"Validated {len(rows)} rows; null actual_spend rows: {len(null_rows)}", file=sys.stderr)
    for row in null_rows:
        print(
            f"NULL: {row['period']} | {row['ward']} | {row['category']} | {row.get('notes', '')}",
            file=sys.stderr,
        )
    return rows


def compute_growth(rows, ward, category, growth_type):
    """Return a per-period table with visible formulas for one ward/category."""
    if not growth_type:
        raise ValueError("growth_type is required; specify MoM or another supported type")
    if growth_type.upper() != "MOM":
        raise ValueError(f"Unsupported growth_type: {growth_type}; only MoM is supported")
    if not ward or not category or ward.lower() in {"all", "any", "*"} or category.lower() in {"all", "any", "*"}:
        raise ValueError("Refusing all-ward or all-category aggregation; specify one ward and category")

    selected = sorted(
        (
            row
            for row in rows
            if _match_key(row["ward"]) == _match_key(ward)
            and _match_key(row["category"]) == _match_key(category)
        ),
        key=lambda row: row["period"],
    )
    if not selected:
        raise ValueError(f"No rows found for ward={ward!r}, category={category!r}")

    result = []
    previous = None
    previous_period = None
    for row in selected:
        current = row["actual_spend"]
        item = {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": "" if current is None else current,
            "growth_type": "MoM",
            "formula": "",
            "growth_percent": "",
            "status": "computed",
            "null_reason": "",
        }
        if current is None:
            item["status"] = "FLAGGED_NULL"
            item["null_reason"] = row.get("notes", "")
        elif previous is None or previous == 0:
            item["status"] = "NOT_COMPUTED_NO_PRIOR_VALUE"
            item["formula"] = f"(({current} - prior_actual_spend) / prior_actual_spend) * 100"
        else:
            item["formula"] = f"(({current} - {previous}) / {previous}) * 100"
            item["growth_percent"] = round((current - previous) / previous * 100, 1)
        result.append(item)
        if current is not None:
            previous = current
            previous_period = row["period"]
    return result


def main():
    parser = argparse.ArgumentParser(description="Compute ward/category budget growth")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    try:
        rows = load_dataset(args.input)
        result = compute_growth(rows, args.ward, args.category, args.growth_type)
        with Path(args.output).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=result[0].keys())
            writer.writeheader()
            writer.writerows(result)
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
