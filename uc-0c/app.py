"""
UC-0C — Number That Looks Right
Computes MoM or YoY growth for a specific ward and category from budget data.
Built using the RICE → agents.md → skills.md → CRAFT workflow.

Enforcement rules from agents.md:
- Never aggregate across wards or categories
- Flag every null row before computing
- Show formula alongside every result
- Refuse if growth-type not specified
"""
import argparse
import csv
import sys


def load_dataset(input_path: str) -> list[dict]:
    """
    Read ward budget CSV, validate columns, report nulls.
    Returns list of row dicts.
    """
    required_columns = ["period", "ward", "category",
                        "budgeted_amount", "actual_spend", "notes"]

    try:
        with open(input_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            # Validate columns
            if reader.fieldnames is None:
                print("Error: CSV file appears to be empty", file=sys.stderr)
                sys.exit(1)

            missing = [c for c in required_columns if c not in reader.fieldnames]
            if missing:
                print(f"Error: Missing required columns: {missing}",
                      file=sys.stderr)
                sys.exit(1)

            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Parse actual_spend and report nulls
    null_rows = []
    for row in rows:
        spend = row.get("actual_spend", "").strip()
        if spend == "" or spend is None:
            row["actual_spend"] = None
            null_rows.append(row)
        else:
            try:
                row["actual_spend"] = float(spend)
            except ValueError:
                row["actual_spend"] = None
                null_rows.append(row)

        # Parse budgeted_amount
        try:
            row["budgeted_amount"] = float(row.get("budgeted_amount", 0))
        except (ValueError, TypeError):
            row["budgeted_amount"] = None

    # Report nulls before returning
    print(f"\n  Dataset loaded: {len(rows)} rows")
    print(f"  Null actual_spend rows: {len(null_rows)}")
    if null_rows:
        print("  -- Null Report --")
        for nr in null_rows:
            reason = nr.get("notes", "No reason provided").strip()
            if not reason:
                reason = "No reason provided"
            print(f"    {nr['period']} | {nr['ward']} | "
                  f"{nr['category']} | Reason: {reason}")
        print("  -- End Null Report --\n")

    return rows


def compute_growth(rows: list[dict], ward: str, category: str,
                   growth_type: str, output_path: str):
    """
    Compute MoM or YoY growth for a specific ward + category.
    Writes results to output CSV.
    """
    # Validate growth_type
    if growth_type not in ("MoM", "YoY"):
        print(f"Error: Invalid growth-type '{growth_type}'. "
              f"Must be 'MoM' or 'YoY'.", file=sys.stderr)
        sys.exit(1)

    # Filter to specified ward and category
    filtered = [r for r in rows
                if r["ward"] == ward and r["category"] == category]

    if not filtered:
        # List available values to help user
        available_wards = sorted(set(r["ward"] for r in rows))
        available_cats = sorted(set(r["category"] for r in rows))
        print(f"Error: No data found for ward='{ward}', "
              f"category='{category}'", file=sys.stderr)
        print(f"  Available wards: {available_wards}", file=sys.stderr)
        print(f"  Available categories: {available_cats}", file=sys.stderr)
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    # Compute growth
    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        actual = row["actual_spend"]
        notes = row.get("notes", "").strip()

        result = {
            "period": period,
            "actual_spend": actual if actual is not None else "NULL",
            "previous_spend": "",
            "formula": "",
            "growth_pct": "",
            "null_flag": "",
            "null_reason": ""
        }

        # First period: no prior data
        if i == 0:
            result["previous_spend"] = "N/A"
            result["formula"] = "N/A (first period)"
            result["growth_pct"] = "N/A"
            if actual is None:
                result["null_flag"] = "NULL"
                result["null_reason"] = notes if notes else "No reason provided"
            results.append(result)
            continue

        # Get previous period data
        if growth_type == "MoM":
            prev_row = filtered[i - 1]
        else:  # YoY — find same month in prior year
            current_year, current_month = period.split("-")
            target_period = f"{int(current_year) - 1}-{current_month}"
            prev_matches = [r for r in filtered if r["period"] == target_period]
            if not prev_matches:
                result["previous_spend"] = "N/A"
                result["formula"] = f"N/A (no data for {target_period})"
                result["growth_pct"] = "N/A"
                if actual is None:
                    result["null_flag"] = "NULL"
                    result["null_reason"] = notes if notes else "No reason provided"
                results.append(result)
                continue
            prev_row = prev_matches[0]

        prev_actual = prev_row["actual_spend"]
        prev_period = prev_row["period"]
        result["previous_spend"] = prev_actual if prev_actual is not None else "NULL"

        # Check for nulls
        if actual is None:
            result["null_flag"] = "NULL"
            result["null_reason"] = notes if notes else "No reason provided"
            result["formula"] = "NOT COMPUTED — current period actual_spend is NULL"
            result["growth_pct"] = "NULL"
            results.append(result)
            continue

        if prev_actual is None:
            prev_notes = prev_row.get("notes", "").strip()
            result["null_flag"] = "NULL"
            result["null_reason"] = (f"Previous period ({prev_period}) "
                                     f"actual_spend is NULL: "
                                     f"{prev_notes if prev_notes else 'No reason'}")
            result["formula"] = "NOT COMPUTED — previous period actual_spend is NULL"
            result["growth_pct"] = "NULL"
            results.append(result)
            continue

        if prev_actual == 0:
            result["formula"] = f"(({actual} - 0) / 0) * 100 — division by zero"
            result["growth_pct"] = "UNDEFINED"
            results.append(result)
            continue

        # Compute growth
        growth = ((actual - prev_actual) / prev_actual) * 100
        result["formula"] = (f"(({actual} - {prev_actual}) / "
                             f"{prev_actual}) * 100")
        result["growth_pct"] = f"{growth:+.1f}%"
        results.append(result)

    # Write output CSV
    fieldnames = ["period", "actual_spend", "previous_spend",
                  "formula", "growth_pct", "null_flag", "null_reason"]
    try:
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        sys.exit(1)

    # Print summary
    computed = [r for r in results
                if r["growth_pct"] not in ("N/A", "NULL", "UNDEFINED", "")]
    null_count = sum(1 for r in results if r["null_flag"] == "NULL")
    print(f"  Ward: {ward}")
    print(f"  Category: {category}")
    print(f"  Growth type: {growth_type}")
    print(f"  Periods: {len(results)}")
    print(f"  Computed: {len(computed)}")
    print(f"  Null-flagged: {null_count}")


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C — Budget Growth Calculator "
                    "(Number That Looks Right)"
    )
    parser.add_argument("--input", required=True,
                        help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True,
                        help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True,
                        help="Budget category (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True,
                        choices=["MoM", "YoY"],
                        help="Growth type: MoM (month-over-month) or "
                             "YoY (year-over-year). REQUIRED — will not guess.")
    parser.add_argument("--output", required=True,
                        help="Path to write growth output CSV")
    args = parser.parse_args()

    print(f"Loading dataset from: {args.input}")
    rows = load_dataset(args.input)

    print(f"Computing {args.growth_type} growth...")
    compute_growth(rows, args.ward, args.category,
                   args.growth_type, args.output)

    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
