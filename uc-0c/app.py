"""
UC-0C — Number That Looks Right
Computes per-ward per-category growth rates from municipal budget data.
Implements agents.md enforcement rules and skills.md skill definitions.
"""
import argparse
import csv
import sys


def load_dataset(file_path: str) -> dict:
    """
    Reads ward budget CSV, validates columns, reports null actual_spend values.
    Returns: dict with 'rows' (list of dicts), 'null_report' (list), and 'metadata' (dict).
    """
    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend"]

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Validate columns
            if reader.fieldnames is None:
                print("ERROR: Empty CSV file", file=sys.stderr)
                sys.exit(1)

            missing = [c for c in required_columns if c not in reader.fieldnames]
            if missing:
                print(f"ERROR: Missing required columns: {missing}", file=sys.stderr)
                sys.exit(1)

            rows = []
            null_report = []
            wards = set()
            categories = set()

            for i, row in enumerate(reader, start=2):
                wards.add(row["ward"])
                categories.add(row["category"])

                # Check for null actual_spend
                actual = row.get("actual_spend", "").strip()
                if actual == "" or actual.lower() == "null":
                    null_report.append({
                        "row": i,
                        "period": row["period"],
                        "ward": row["ward"],
                        "category": row["category"],
                        "reason": row.get("notes", "No reason provided").strip()
                    })
                    row["actual_spend"] = None
                else:
                    try:
                        row["actual_spend"] = float(actual)
                    except ValueError:
                        null_report.append({
                            "row": i,
                            "period": row["period"],
                            "ward": row["ward"],
                            "category": row["category"],
                            "reason": f"Invalid numeric value: {actual}"
                        })
                        row["actual_spend"] = None

                rows.append(row)

    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    metadata = {
        "total_rows": len(rows),
        "null_count": len(null_report),
        "unique_wards": sorted(wards),
        "unique_categories": sorted(categories)
    }

    # Report nulls upfront
    if null_report:
        print(f"\n⚠ NULL REPORT: {len(null_report)} rows with missing actual_spend:")
        for nr in null_report:
            reason = nr['reason'] if nr['reason'] else 'No reason'
            print(f"  - {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {reason}")
        print()

    return {"rows": rows, "null_report": null_report, "metadata": metadata}


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str) -> list:
    """
    Computes growth rate for a specific ward+category combination.
    Returns: list of period records with growth calculations.

    Enforcement:
    - Refuses cross-ward aggregation
    - Flags null rows
    - Shows formula per row
    - Refuses if growth_type not specified
    """
    metadata = dataset["metadata"]

    # Validate ward
    if ward not in metadata["unique_wards"]:
        print(f"ERROR: Ward '{ward}' not found. Valid wards:", file=sys.stderr)
        for w in metadata["unique_wards"]:
            print(f"  - {w}", file=sys.stderr)
        sys.exit(1)

    # Validate category
    if category not in metadata["unique_categories"]:
        print(f"ERROR: Category '{category}' not found. Valid categories:", file=sys.stderr)
        for c in metadata["unique_categories"]:
            print(f"  - {c}", file=sys.stderr)
        sys.exit(1)

    # Validate growth type
    if growth_type not in ("MoM", "YoY"):
        print("ERROR: Please specify growth type: MoM (month-over-month) or YoY (year-over-year).", file=sys.stderr)
        sys.exit(1)

    # Filter to specified ward and category
    filtered = [
        r for r in dataset["rows"]
        if r["ward"] == ward and r["category"] == category
    ]

    # Sort by period
    filtered.sort(key=lambda x: x["period"])

    # Compute growth
    results = []
    prev_value = None
    prev_was_null = False

    for i, row in enumerate(filtered):
        period = row["period"]
        actual = row["actual_spend"]
        record = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual,
            "formula": "",
            "growth_rate": "",
            "flag": ""
        }

        if actual is None:
            # Null row — flag it
            notes = row.get("notes", "").strip()
            record["actual_spend"] = "NULL"
            record["formula"] = "N/A"
            record["growth_rate"] = "N/A"
            record["flag"] = f"NULL value — reason: {notes if notes else 'not specified'}"
            prev_was_null = True
            prev_value = None
        elif i == 0:
            # First period — no previous value
            record["formula"] = "N/A (first period)"
            record["growth_rate"] = "N/A"
            record["flag"] = "No previous period for comparison"
            prev_value = actual
            prev_was_null = False
        elif prev_was_null:
            # Previous period was null — cannot compute
            record["formula"] = f"{growth_type} = (current - previous) / previous × 100"
            record["growth_rate"] = "N/A"
            record["flag"] = "Previous period null — growth not computable"
            prev_value = actual
            prev_was_null = False
        elif prev_value is not None and prev_value != 0:
            # Normal calculation
            growth = ((actual - prev_value) / prev_value) * 100
            record["formula"] = f"{growth_type} = ({actual} - {prev_value}) / {prev_value} × 100"
            record["growth_rate"] = f"{growth:+.1f}%"
            record["flag"] = ""
            prev_value = actual
            prev_was_null = False
        elif prev_value == 0:
            record["formula"] = f"{growth_type} = ({actual} - 0) / 0 × 100"
            record["growth_rate"] = "N/A"
            record["flag"] = "Division by zero — previous period was 0"
            prev_value = actual
            prev_was_null = False

        results.append(record)

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (exact match)")
    parser.add_argument("--category", required=True, help="Category name (exact match)")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                        help="Growth type: MoM (month-over-month) or YoY (year-over-year)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Skill 1: Load and validate dataset
    dataset = load_dataset(args.input)
    print(f"Dataset loaded: {dataset['metadata']['total_rows']} rows, "
          f"{dataset['metadata']['null_count']} nulls detected.")

    # Refuse cross-ward aggregation
    print(f"\nComputing {args.growth_type} growth for:")
    print(f"  Ward: {args.ward}")
    print(f"  Category: {args.category}")
    print()

    # Skill 2: Compute growth
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)

    # Write output CSV
    fieldnames = ["period", "ward", "category", "actual_spend", "formula", "growth_rate", "flag"]
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth output written to {args.output}")
    print(f"Periods computed: {len(results)}")

    # Report flagged rows
    flagged = [r for r in results if r["flag"]]
    if flagged:
        print(f"\n⚠ Flagged periods ({len(flagged)}):")
        for r in flagged:
            print(f"  {r['period']}: {r['flag']}")


if __name__ == "__main__":
    main()
