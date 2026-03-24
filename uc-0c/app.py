"""
UC-0C — Number That Looks Right
Reads ward_budget.csv and computes MoM or YoY growth per ward per category.
Never aggregates across wards. Flags all null rows before computing.
"""
import argparse
import csv
from collections import defaultdict


REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(file_path: str):
    """
    Reads ward_budget.csv, validates columns, reports all null rows before returning data.
    Returns: (rows, null_report) or (None, None) on error.
    """
    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = set(reader.fieldnames or [])
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}")
        return None, None

    # Validate columns
    missing = REQUIRED_COLUMNS - fieldnames
    if missing:
        print(f"ERROR: Missing required columns: {', '.join(sorted(missing))}")
        print(f"       Found columns: {', '.join(sorted(fieldnames))}")
        return None, None

    # Find null rows BEFORE any computation
    null_report = []
    for row in rows:
        if row.get("actual_spend", "").strip() == "":
            null_report.append({
                "period":   row["period"],
                "ward":     row["ward"],
                "category": row["category"],
                "reason":   row.get("notes", "No reason provided").strip() or "No reason provided",
            })

    print(f"\nLoaded {len(rows)} rows from {file_path}")
    print(f"\n--- NULL REPORT ({len(null_report)} rows with missing actual_spend) ---")
    if null_report:
        for n in null_report:
            print(f"  NULL: {n['period']} | {n['ward']} | {n['category']} | Reason: {n['reason']}")
    else:
        print("  No null rows found.")
    print("")

    return rows, null_report


def compute_growth(rows, ward: str, category: str, growth_type: str, output_path: str):
    """
    Computes MoM or YoY growth for a specific ward + category.
    Writes output CSV with period, actual_spend, growth_value, formula_used, null_flag.
    """
    if not growth_type:
        print("ERROR: --growth-type not specified. Please specify 'MoM' or 'YoY'. Never guessed.")
        return

    growth_type = growth_type.upper()
    if growth_type not in ("MOM", "YOY"):
        print(f"ERROR: Invalid growth type '{growth_type}'. Must be 'MoM' or 'YoY'.")
        return

    # Validate ward and category exist
    valid_wards = sorted(set(r["ward"] for r in rows))
    valid_categories = sorted(set(r["category"] for r in rows))

    if ward not in valid_wards:
        print(f"ERROR: Ward '{ward}' not found in dataset.")
        print(f"       Valid wards: {', '.join(valid_wards)}")
        return

    if category not in valid_categories:
        print(f"ERROR: Category '{category}' not found in dataset.")
        print(f"       Valid categories: {', '.join(valid_categories)}")
        return

    # Filter rows for this ward + category
    filtered = [
        r for r in rows
        if r["ward"] == ward and r["category"] == category
    ]
    filtered.sort(key=lambda r: r["period"])

    if not filtered:
        print(f"ERROR: No data found for ward='{ward}' category='{category}'")
        return

    print(f"Computing {growth_type} growth for: {ward} | {category}")
    print(f"Found {len(filtered)} rows\n")

    # Build a lookup: period -> actual_spend (None if null)
    spend_by_period = {}
    for r in filtered:
        val = r.get("actual_spend", "").strip()
        spend_by_period[r["period"]] = float(val) if val else None

    # Compute growth
    results = []
    for r in filtered:
        period = r["period"]
        actual = spend_by_period.get(period)
        null_flag = "TRUE" if actual is None else ""

        if actual is None:
            results.append({
                "period":       period,
                "ward":         ward,
                "category":     category,
                "actual_spend": "",
                "growth_value": "",
                "formula_used": "N/A — null row",
                "null_flag":    "TRUE",
                "notes":        r.get("notes", ""),
            })
            continue

        # Find comparison period
        if growth_type == "MOM":
            # Previous month
            year, month = int(period[:4]), int(period[5:7])
            if month == 1:
                prev_period = f"{year-1}-12"
            else:
                prev_period = f"{year}-{month-1:02d}"
            prev_actual = spend_by_period.get(prev_period)
            formula_template = f"(({period} - {prev_period}) / {prev_period}) x 100"
        else:  # YOY
            year, month = int(period[:4]), int(period[5:7])
            prev_period = f"{year-1}-{month:02d}"
            prev_actual = spend_by_period.get(prev_period)
            formula_template = f"(({period} - {prev_period}) / {prev_period}) x 100"

        if prev_actual is None:
            growth_value = ""
            formula_used = f"N/A — comparison period {prev_period} is null or not in dataset"
        elif prev_actual == 0:
            growth_value = ""
            formula_used = f"N/A — previous period value is 0, cannot divide"
        else:
            growth = ((actual - prev_actual) / prev_actual) * 100
            growth_value = f"{growth:+.1f}%"
            formula_used = f"(({actual} - {prev_actual}) / {prev_actual}) x 100 = {growth_value}"

        results.append({
            "period":       period,
            "ward":         ward,
            "category":     category,
            "actual_spend": actual,
            "growth_value": growth_value,
            "formula_used": formula_used,
            "null_flag":    null_flag,
            "notes":        r.get("notes", ""),
        })

    # Print summary to terminal
    print(f"{'Period':<12} {'Actual Spend':>14} {'Growth':>10}  Formula")
    print("-" * 72)
    for r in results:
        spend_str = f"Rs {r['actual_spend']} lakh" if r["actual_spend"] != "" else "NULL"
        print(f"{r['period']:<12} {spend_str:>14} {str(r['growth_value']):>10}  {r['formula_used']}")

    # Write output CSV
    fieldnames = ["period", "ward", "category", "actual_spend",
                  "growth_value", "formula_used", "null_flag", "notes"]
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"\nOutput written to {output_path}")
    except Exception as e:
        print(f"ERROR: Could not write output: {e}")


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyser")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Ward name e.g. 'Ward 1 - Kasba'")
    parser.add_argument("--category",    required=True,  help="Category e.g. 'Roads & Pothole Repair'")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY", dest="growth_type")
    parser.add_argument("--output",      required=True,  help="Path to write growth_output.csv")
    args = parser.parse_args()

    if not args.growth_type:
        print("ERROR: --growth-type not specified. Please specify MoM or YoY. Refusing to guess.")
        return

    rows, null_report = load_dataset(args.input)
    if rows is None:
        return

    compute_growth(rows, args.ward, args.category, args.growth_type, args.output)


if __name__ == "__main__":
    main()