```python
"""
UC-0C — Number That Looks Right
Municipal budget growth calculator with strict null handling and formula transparency.
"""
import argparse
import csv
import sys


REQUIRED_COLUMNS = [
    "period", "ward", "category",
    "budgeted_amount", "actual_spend", "notes",
]


def load_dataset(path: str):
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            if not reader.fieldnames:
                print("ERROR: CSV has no header row.", file=sys.stderr)
                sys.exit(1)

            missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
            if missing:
                print(f"ERROR: Missing required columns: {missing}", file=sys.stderr)
                sys.exit(1)

            rows = list(reader)

    except FileNotFoundError:
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Cannot read file: {e}", file=sys.stderr)
        sys.exit(1)

    if not rows:
        print("ERROR: CSV has no data rows.", file=sys.stderr)
        sys.exit(1)

    # Parse numeric fields
    for row in rows:
        row["budgeted_amount"] = float(row["budgeted_amount"]) if row["budgeted_amount"].strip() else None
        row["actual_spend"] = float(row["actual_spend"]) if row["actual_spend"].strip() else None

    # Build null report
    null_report = []
    for i, row in enumerate(rows):
        if row["actual_spend"] is None:
            null_report.append({
                "row_index": i,
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "reason": row["notes"] if row["notes"].strip() else "No reason given",
            })

    return rows, null_report


def compute_growth(data, ward, category, growth_type, null_report):
    # Validations
    if not growth_type:
        print("ERROR: --growth-type is required.", file=sys.stderr)
        sys.exit(1)

    if growth_type not in ("MoM", "YoY"):
        print("ERROR: growth-type must be MoM or YoY.", file=sys.stderr)
        sys.exit(1)

    if not ward:
        print("ERROR: --ward is required.", file=sys.stderr)
        sys.exit(1)

    if not category:
        print("ERROR: --category is required.", file=sys.stderr)
        sys.exit(1)

    # Filter strictly (no aggregation)
    filtered = [r for r in data if r["ward"] == ward and r["category"] == category]

    if not filtered:
        print("ERROR: No matching data found.", file=sys.stderr)
        sys.exit(1)

    # Sort chronologically
    filtered.sort(key=lambda r: r["period"])

    # Null lookup
    null_map = {
        (nr["period"], nr["ward"], nr["category"]): nr["reason"]
        for nr in null_report
    }

    results = []

    for i, row in enumerate(filtered):
        period = row["period"]
        actual = row["actual_spend"]

        entry = {
            "ward": ward,
            "category": category,
            "period": period,
            "budgeted_amount": row["budgeted_amount"],
            "actual_spend": actual,
            "prev_spend": None,
            "growth_percent": None,
            "formula": "",
            "status": "",
        }

        # NULL CURRENT
        if (period, ward, category) in null_map:
            entry["status"] = f"NULL FLAG — {null_map[(period, ward, category)]}"
            entry["formula"] = "N/A"
            results.append(entry)
            continue

        if actual is None:
            entry["status"] = "NULL FLAG — missing actual_spend"
            entry["formula"] = "N/A"
            results.append(entry)
            continue

        # MoM
        if growth_type == "MoM":
            if i == 0:
                entry["status"] = "No previous data"
                entry["formula"] = "N/A"
            else:
                prev_row = filtered[i - 1]
                prev_val = prev_row["actual_spend"]
                entry["prev_spend"] = prev_val

                if prev_val is None:
                    entry["status"] = f"NULL FLAG — Previous period ({prev_row['period']}) is NULL"
                    entry["formula"] = "N/A"
                else:
                    growth = ((actual - prev_val) / prev_val) * 100
                    entry["growth_percent"] = round(growth, 1)
                    entry["formula"] = f"({actual} - {prev_val}) / {prev_val} x 100"
                    entry["status"] = "OK"

        # YoY
        elif growth_type == "YoY":
            year, month = period.split("-")
            prev_period = f"{int(year) - 1}-{month}"

            prev_row = next(
                (r for r in data if r["period"] == prev_period and r["ward"] == ward and r["category"] == category),
                None
            )

            if prev_row:
                prev_val = prev_row["actual_spend"]
                entry["prev_spend"] = prev_val

                if prev_val is None:
                    entry["status"] = f"NULL FLAG — Previous year ({prev_period}) is NULL"
                    entry["formula"] = "N/A"
                else:
                    growth = ((actual - prev_val) / prev_val) * 100
                    entry["growth_percent"] = round(growth, 1)
                    entry["formula"] = f"({actual} - {prev_val}) / {prev_val} x 100"
                    entry["status"] = "OK"
            else:
                entry["status"] = f"No data for previous year ({prev_period})"
                entry["formula"] = "N/A"

        results.append(entry)

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    data, null_report = load_dataset(args.input)

    # Print null report
    if null_report:
        print(f"NULL REPORT: {len(null_report)} rows found", file=sys.stderr)
        for nr in null_report:
            print(f"{nr['period']} | {nr['ward']} | {nr['category']} | {nr['reason']}", file=sys.stderr)
        print(file=sys.stderr)

    results = compute_growth(
        data,
        args.ward,
        args.category,
        args.growth_type,
        null_report
    )

    fieldnames = [
        "ward",
        "category",
        "period",
        "budgeted_amount",
        "actual_spend",
        "prev_spend",
        "growth_percent",
        "formula",
        "status",
    ]

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Output written to {args.output}")
    print(f"Ward: {args.ward} | Category: {args.category} | Growth: {args.growth_type}")


if __name__ == "__main__":
    main()
```
