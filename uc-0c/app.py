"""
UC-0C app.py -- Budget Growth Analyst
Computes per-ward per-category MoM/YoY growth with null flagging and formula transparency.
Implements: agents.md (enforcement rules) + skills.md (load_dataset, compute_growth).
"""
import argparse
import csv
import sys


# ---------------------------------------------------------------------------
# Skill: load_dataset
# ---------------------------------------------------------------------------
def load_dataset(filepath):
    """
    Reads ward_budget.csv, validates expected columns, performs mandatory
    null scan on actual_spend before returning parsed data.

    Returns:
        dict with keys:
          rows        - list of parsed row dicts (actual_spend is float or None)
          null_report - list of dicts for each null actual_spend row
          null_count  - int
    """
    expected_columns = {
        "period", "ward", "category",
        "budgeted_amount", "actual_spend", "notes"
    }

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = set(reader.fieldnames or [])

            # Abort if expected columns are missing
            missing = expected_columns - headers
            if missing:
                print(f"ERROR: Missing expected columns: {missing}")
                sys.exit(1)

            rows = []
            null_report = []

            for line_num, row in enumerate(reader, start=2):
                raw_spend = row.get("actual_spend", "").strip()
                actual_spend = None if raw_spend == "" else float(raw_spend)

                parsed = {
                    "period":          row["period"].strip(),
                    "ward":            row["ward"].strip(),
                    "category":        row["category"].strip(),
                    "budgeted_amount": float(row["budgeted_amount"].strip()),
                    "actual_spend":    actual_spend,
                    "notes":           row.get("notes", "").strip(),
                }
                rows.append(parsed)

                # Never silently drop nulls -- record every one
                if actual_spend is None:
                    null_report.append({
                        "line":     line_num,
                        "period":   parsed["period"],
                        "ward":     parsed["ward"],
                        "category": parsed["category"],
                        "reason":   parsed["notes"] or "No reason provided",
                    })

    except FileNotFoundError:
        print(f"ERROR: File not found -- {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to read file -- {e}")
        sys.exit(1)

    # --- NULL PREFLIGHT (agents.md: NULL_PREFLIGHT) ---
    null_count = len(null_report)
    print("\n=== NULL PREFLIGHT REPORT ===")
    print(f"Total rows loaded: {len(rows)}")
    print(f"Null actual_spend values found: {null_count}")
    if null_count > 0:
        for entry in null_report:
            print(
                f"  [!] NULL at {entry['period']} | "
                f"{entry['ward']} | {entry['category']} | "
                f"Reason: {entry['reason']}"
            )
    print()

    return {"rows": rows, "null_report": null_report, "null_count": null_count}


# ---------------------------------------------------------------------------
# Skill: compute_growth
# ---------------------------------------------------------------------------
def compute_growth(data, ward, category, growth_type):
    """
    Computes per-period growth for exactly one ward and one category.

    Args:
        data        - output from load_dataset
        ward        - exact ward name string
        category    - exact category name string
        growth_type - 'MoM' or 'YoY' (must be explicitly provided)

    Returns:
        list of dicts with keys: period, ward, category,
        actual_spend, growth, formula
    """
    rows = data["rows"]

    # --- AGGREGATION_BLOCK: validate single ward + category ---
    all_wards = sorted(set(r["ward"] for r in rows))
    all_categories = sorted(set(r["category"] for r in rows))

    if ward not in all_wards:
        print(f"ERROR: Ward '{ward}' not found in dataset.")
        print(f"  Available wards: {all_wards}")
        sys.exit(1)

    if category not in all_categories:
        print(f"ERROR: Category '{category}' not found in dataset.")
        print(f"  Available categories: {all_categories}")
        sys.exit(1)

    # Filter to exactly one ward + one category
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    filtered.sort(key=lambda r: r["period"])

    if not filtered:
        print(f"ERROR: No data found for ward='{ward}', category='{category}'.")
        sys.exit(1)

    # Period offset
    if growth_type == "MoM":
        offset = 1
    elif growth_type == "YoY":
        offset = 12
    else:
        print(f"ERROR: Unsupported growth_type '{growth_type}'. Must be 'MoM' or 'YoY'.")
        sys.exit(1)

    # --- Report nulls in this ward+category slice ---
    null_in_slice = [r for r in filtered if r["actual_spend"] is None]
    if null_in_slice:
        print(f"=== NULL VALUES IN {ward} / {category} ===")
        for r in null_in_slice:
            reason = r["notes"] or "No reason provided"
            print(f"  [!] {r['period']}: actual_spend is NULL -- {reason}")
        print()

    # --- Compute growth row by row ---
    results = []

    for i, row in enumerate(filtered):
        result = {
            "period":       row["period"],
            "ward":         ward,
            "category":     category,
            "actual_spend": row["actual_spend"],
            "growth":       "",
            "formula":      "",
        }

        # No prior period available
        if i < offset:
            if row["actual_spend"] is None:
                reason = row["notes"] or "No reason provided"
                result["growth"]  = "NULL -- not computed"
                result["formula"] = f"Reason: {reason}"
            else:
                result["growth"]  = "N/A"
                result["formula"] = f"No prior period for {growth_type}"
            results.append(result)
            continue

        prev_row = filtered[i - offset]

        # --- NULL_HALT: current is null ---
        if row["actual_spend"] is None:
            reason = row["notes"] or "No reason provided"
            result["growth"]  = "NULL -- not computed"
            result["formula"] = f"Reason: {reason}"
            results.append(result)
            continue

        # --- NULL_HALT: previous is null ---
        if prev_row["actual_spend"] is None:
            prev_reason = prev_row["notes"] or "No reason provided"
            result["growth"]  = "NULL -- not computed"
            result["formula"] = (
                f"Previous period ({prev_row['period']}) "
                f"actual_spend is NULL -- {prev_reason}"
            )
            results.append(result)
            continue

        # --- Compute with formula ---
        current  = row["actual_spend"]
        previous = prev_row["actual_spend"]

        if previous == 0:
            result["growth"]  = "ERR"
            result["formula"] = "Division by zero -- previous actual_spend is 0"
            results.append(result)
            continue

        growth_pct = round(((current - previous) / previous) * 100, 1)
        sign = "+" if growth_pct >= 0 else ""

        result["growth"]  = f"{sign}{growth_pct}%"
        result["formula"] = f"(({current} - {previous}) / {previous}) * 100 = {sign}{growth_pct}%"

        results.append(result)

    return results


# ---------------------------------------------------------------------------
# Output writer
# ---------------------------------------------------------------------------
def write_output(results, output_path):
    """Writes results to CSV with columns: period, ward, category, actual_spend, growth, formula."""
    fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            out = dict(row)
            if out["actual_spend"] is None:
                out["actual_spend"] = ""
            writer.writerow(out)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Analyst -- per-ward per-category growth"
    )
    parser.add_argument("--input",    required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward",     required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument(
        "--growth-type", dest="growth_type", default=None,
        help="Growth type: MoM or YoY (REQUIRED -- will refuse if missing)"
    )
    parser.add_argument("--output",   required=True, help="Path to output CSV")
    args = parser.parse_args()

    # --- GROWTH_TYPE_REQUIRED: refuse if missing ---
    if args.growth_type is None:
        print("ERROR: --growth-type is REQUIRED. Please specify 'MoM' or 'YoY'.")
        print("  Refusing to proceed -- the system will never assume a growth type.")
        sys.exit(1)

    if args.growth_type not in ("MoM", "YoY"):
        print(f"ERROR: Invalid growth-type '{args.growth_type}'. Must be 'MoM' or 'YoY'.")
        sys.exit(1)

    print("UC-0C Budget Growth Analyst")
    print(f"  Ward:        {args.ward}")
    print(f"  Category:    {args.category}")
    print(f"  Growth Type: {args.growth_type}")
    print(f"  Input:       {args.input}")
    print(f"  Output:      {args.output}")

    # Step 1 -- load_dataset (null preflight)
    data = load_dataset(args.input)

    # Step 2 -- compute_growth (single ward + category, no aggregation)
    results = compute_growth(data, args.ward, args.category, args.growth_type)

    # Step 3 -- Console output
    print(f"=== GROWTH OUTPUT: {args.ward} / {args.category} ({args.growth_type}) ===")
    for r in results:
        spend = f"Rs.{r['actual_spend']} lakh" if r["actual_spend"] is not None else "NULL"
        print(f"  {r['period']} | {spend} | {r['growth']} | {r['formula']}")
    print()

    # Step 4 -- Write CSV
    write_output(results, args.output)
    print(f"Output written to {args.output}")


if __name__ == "__main__":
    main()
