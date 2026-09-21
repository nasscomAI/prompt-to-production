"""UC-0C ward-level month-over-month growth calculator."""
import argparse
import csv
from decimal import Decimal, InvalidOperation

REQUIRED_COLUMNS = {
    "period", "ward", "category", "budgeted_amount", "actual_spend", "notes",
}


def load_dataset(input_path):
    with open(input_path, "r", newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError("Missing required columns: {}".format(", ".join(sorted(missing))))
        rows = []
        for line_number, row in enumerate(reader, start=2):
            try:
                budgeted = Decimal(row["budgeted_amount"])
                actual = None if not row["actual_spend"].strip() else Decimal(row["actual_spend"])
            except (AttributeError, InvalidOperation):
                raise ValueError("Invalid numeric value on input row {}".format(line_number))
            row["_budgeted"] = budgeted
            row["_actual"] = actual
            rows.append(row)
    return rows


def compute_growth(rows, ward, category, growth_type):
    if not growth_type:
        raise ValueError("--growth-type is required; refusing to guess a formula")
    if growth_type != "MoM":
        raise ValueError("Unsupported growth type {!r}; only MoM is supported".format(growth_type))
    if not ward or ward.lower() in ("all", "all wards"):
        raise ValueError("A specific ward is required; all-ward aggregation is refused")
    if not category or category.lower() in ("all", "all categories"):
        raise ValueError("A specific category is required; all-category aggregation is refused")
    selected = sorted(
        (row for row in rows if row["ward"] == ward and row["category"] == category),
        key=lambda row: row["period"],
    )
    if not selected:
        raise ValueError("No rows found for the requested ward and category")
    results = []
    previous = None
    for row in selected:
        actual = row["_actual"]
        formula = "MoM growth = ((current - previous) / previous) * 100"
        status = "OK"
        growth = ""
        if actual is None:
            status = "NULL_CURRENT"
            null_reason = row["notes"].strip() or "actual_spend is blank"
        elif previous is None:
            status = "NO_PRIOR_VALUE"
            null_reason = ""
        elif previous["_actual"] is None:
            status = "NULL_PRIOR"
            null_reason = previous["notes"].strip() or "prior actual_spend is blank"
        elif previous["_actual"] == 0:
            status = "UNDEFINED_ZERO_PRIOR"
            null_reason = "prior actual_spend is zero"
        else:
            growth = "{:.1f}".format((actual - previous["_actual"]) / previous["_actual"] * 100)
            null_reason = ""
        results.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": "" if actual is None else "{:.1f}".format(actual),
            "previous_actual_spend": (
                "" if previous is None or previous["_actual"] is None
                else "{:.1f}".format(previous["_actual"])
            ),
            "growth_type": growth_type,
            "formula": formula,
            "growth_percent": growth,
            "status": status,
            "null_reason": null_reason,
        })
        previous = row
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C ward budget growth calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    fields = list(results[0])
    with open(args.output, "w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    null_count = sum(1 for row in rows if row["_actual"] is None)
    print("Loaded {} rows; flagged {} null actual_spend rows.".format(len(rows), null_count))
    print("Wrote {} rows to {}".format(len(results), args.output))


if __name__ == "__main__":
    main()
