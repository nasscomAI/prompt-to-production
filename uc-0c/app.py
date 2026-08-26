"""
UC-0C app.py — Number That Looks Right
Build this using the RICE + agents.md + CRAFT workflow.
"""
import argparse
import csv
import sys


def load_dataset(input_file):
    """Reads CSV, validates columns, reports null count and which rows before returning."""
    try:
        with open(input_file, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
            if not required_columns.issubset(reader.fieldnames):
                missing = required_columns - set(reader.fieldnames)
                raise ValueError(f"Missing columns: {missing}")
            rows = list(reader)
    except FileNotFoundError:
        raise ValueError(f"File not found: {input_file}")

    null_rows = []
    for i, row in enumerate(rows):
        if row["actual_spend"].strip() == "" or row["actual_spend"] is None:
            null_rows.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "notes": row["notes"].strip(),
            })

    report = {
        "total_rows": len(rows),
        "null_count": len(null_rows),
        "null_rows": null_rows,
    }
    return rows, report


def compute_growth(ward, category, growth_type, data):
    """Takes ward + category + growth_type, returns per-period table with formula shown."""
    rows = [r for r in data if r["ward"] == ward and r["category"] == category]
    if not rows:
        raise ValueError(f"No data found for ward='{ward}', category='{category}'")

    # Sort by period
    rows.sort(key=lambda r: r["period"])

    # Filter out null actual_spend rows
    valid_rows = []
    for row in rows:
        if row["actual_spend"].strip() == "":
            valid_rows.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": None,
                "growth": None,
                "formula": "NULL — not computed",
                "null_flag": True,
            })
        else:
            valid_rows.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": float(row["actual_spend"]),
                "growth": None,
                "formula": "",
                "null_flag": False,
            })

    # Compute growth
    for i in range(len(valid_rows)):
        if valid_rows[i]["null_flag"]:
            continue
        if i == 0:
            valid_rows[i]["growth"] = None
            valid_rows[i]["formula"] = "MoM growth: N/A (first period)"
        else:
            prev = valid_rows[i - 1]["actual_spend"]
            curr = valid_rows[i]["actual_spend"]
            if prev is None:
                growth_pct = None
                formula = "MoM growth: N/A (previous period null)"
            elif prev == 0:
                growth_pct = None
                formula = "MoM growth: division by zero (prev=0)"
            else:
                growth_pct = ((curr - prev) / prev) * 100
                formula = f"MoM growth: (({curr} - {prev}) / {prev}) * 100 = {growth_pct:.1f}%"
            valid_rows[i]["growth"] = growth_pct
            valid_rows[i]["formula"] = formula

    # Check for across-wards/categories aggregation attempt
    wards_in_set = set(r["ward"] for r in rows)
    categories_in_set = set(r["category"] for r in rows)
    if len(wards_in_set) > 1 or len(categories_in_set) > 1:
        raise ValueError(
            "All-ward aggregation → system must REFUSE — query specifies single ward and category"
        )

    return valid_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C: Number That Looks Right")
    parser.add_argument("--input", required=True, help="Path to budget CSV file")
    parser.add_argument("--ward", required=True, help="Ward name filter")
    parser.add_argument("--category", required=True, help="Category name filter")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                        help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Output CSV file path")

    args = parser.parse_args()

    # Load dataset
    data, report = load_dataset(args.input)
    print(f"Loaded {report['total_rows']} rows, {report['null_count']} null values flagged")

    # Report null rows
    for nr in report["null_rows"]:
        print(f"  NULL: {nr['period']} · {nr['ward']} · {nr['category']} · {nr['notes']}")

    # Compute growth
    try:
        result = compute_growth(args.ward, args.category, args.growth_type, data)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Write output
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "ward", "category", "actual_spend", "growth", "formula", "null_flag"])
        for row in result:
            writer.writerow([
                row["period"],
                row["ward"],
                row["category"],
                row["actual_spend"] if row["actual_spend"] is not None else "",
                row["growth"] if row["growth"] is not None else "",
                row["formula"],
                row["null_flag"],
            ])

    print(f"Output written to {args.output}")


if __name__ == "__main__":
    main()