"""
UC-0C — Number That Looks Right
Built using RICE → agents.md → skills.md → CRAFT workflow.
Computes per-ward per-category growth with null flagging and formula transparency.
"""
import argparse
import csv
import sys

EXPECTED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(input_path: str) -> tuple:
    """
    Reads the budget CSV, validates columns, and reports null counts and affected
    rows before returning data.
    Returns: (rows, null_report) where null_report is a list of dicts describing null rows.
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # Validate columns
            missing = [c for c in EXPECTED_COLUMNS if c not in reader.fieldnames]
            if missing:
                print(f"Error: Missing expected columns: {', '.join(missing)}", file=sys.stderr)
                sys.exit(1)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Report nulls before any computation
    null_report = []
    for row in rows:
        if row["actual_spend"].strip() == "":
            null_report.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "reason": row["notes"].strip() if row["notes"] else "No reason provided",
            })

    if null_report:
        print(f"\n=== NULL REPORT: {len(null_report)} null actual_spend rows found ===")
        for nr in null_report:
            print(f"  {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['reason']}")
        print()

    return rows, null_report


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes period-over-period growth for a specific ward and category.
    Returns a list of result dicts with formula shown for each row.
    """
    # Validate ward and category exist
    valid_wards = sorted(set(r["ward"] for r in rows))
    valid_categories = sorted(set(r["category"] for r in rows))

    if ward not in valid_wards:
        print(f"Error: Ward '{ward}' not found. Valid wards:", file=sys.stderr)
        for w in valid_wards:
            print(f"  - {w}", file=sys.stderr)
        sys.exit(1)

    if category not in valid_categories:
        print(f"Error: Category '{category}' not found. Valid categories:", file=sys.stderr)
        for c in valid_categories:
            print(f"  - {c}", file=sys.stderr)
        sys.exit(1)

    # Filter and sort by period
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    filtered.sort(key=lambda r: r["period"])

    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        actual_raw = row["actual_spend"].strip()
        notes = row["notes"].strip() if row["notes"] else ""

        # Handle null actual_spend
        if actual_raw == "":
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "previous_spend": "",
                "growth_percent": "NULL — not computed",
                "formula_used": f"Null actual_spend: {notes}",
            })
            continue

        actual = float(actual_raw)

        # First period has no previous to compare
        if i == 0:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": str(actual),
                "previous_spend": "",
                "growth_percent": "N/A — first period",
                "formula_used": "No previous period for comparison",
            })
            continue

        # Check if previous period was null
        prev_raw = filtered[i - 1]["actual_spend"].strip()
        if prev_raw == "":
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": str(actual),
                "previous_spend": "NULL",
                "growth_percent": "NULL — not computed",
                "formula_used": "Previous period actual_spend is null — cannot compute growth",
            })
            continue

        prev = float(prev_raw)

        if growth_type == "MoM":
            if prev == 0:
                growth_pct = "undefined (division by zero)"
                formula = f"({actual} - 0) / 0 * 100 = undefined"
            else:
                growth_val = (actual - prev) / prev * 100
                growth_pct = f"{growth_val:+.1f}%"
                formula = f"({actual} - {prev}) / {prev} * 100 = {growth_val:+.1f}%"
        else:
            # This shouldn't happen since we validate growth_type in main
            growth_pct = "unsupported"
            formula = f"Unsupported growth type: {growth_type}"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": str(actual),
            "previous_spend": str(prev),
            "growth_percent": growth_pct,
            "formula_used": formula,
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyzer")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to filter on")
    parser.add_argument("--category", required=True, help="Category to filter on")
    parser.add_argument("--growth-type", dest="growth_type", default=None,
                        help="Growth formula type (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforcement: refuse if growth-type not specified
    if not args.growth_type:
        print("Error: --growth-type is required. Please specify a growth type (e.g., MoM).", file=sys.stderr)
        print("Usage example: --growth-type MoM", file=sys.stderr)
        sys.exit(1)

    # Skill 1: load_dataset
    rows, null_report = load_dataset(args.input)
    print(f"Loaded {len(rows)} rows from {args.input}")

    # Skill 2: compute_growth
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    # Write output CSV
    fieldnames = ["period", "ward", "category", "actual_spend", "previous_spend",
                  "growth_percent", "formula_used"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth output written to {args.output}")


if __name__ == "__main__":
    main()
