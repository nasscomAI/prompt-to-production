"""
UC-0C — Number That Looks Right
Rule-based budget growth calculator built using the RICE → agents.md → skills.md → CRAFT workflow.
Computes per-ward per-category MoM or YoY growth with null flagging and formula transparency.
"""
import argparse
import csv
import sys


# ── Skill: load_dataset ──────────────────────────────────────────────────────

def load_dataset(file_path: str) -> list:
    """
    Read ward budget CSV data, validate columns, report nulls before returning data.
    Returns list of row dicts with all fields preserved.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Validate required columns
    required = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    if rows:
        present = set(rows[0].keys())
        missing = required - present
        if missing:
            print(f"ERROR: Missing required columns: {missing}", file=sys.stderr)
            sys.exit(1)

    # Null report (Enforcement Rule 2)
    null_rows = []
    for row in rows:
        if not row.get("actual_spend") or row["actual_spend"].strip() == "":
            null_rows.append(row)

    print(f"Loaded {len(rows)} rows from {file_path}.")
    if null_rows:
        print(f"\n[!] NULL REPORT -- {len(null_rows)} rows with missing actual_spend:")
        print(f"{'Period':<12} {'Ward':<28} {'Category':<28} {'Reason'}")
        print("-" * 100)
        for nr in null_rows:
            note = nr.get("notes", "No reason given").strip()
            if not note:
                note = "No reason given"
            print(f"{nr['period']:<12} {nr['ward']:<28} {nr['category']:<28} {note}")
        print()
    else:
        print("No null actual_spend values found.\n")

    return rows


# ── Skill: compute_growth ────────────────────────────────────────────────────

def compute_growth(data: list, ward: str, category: str, growth_type: str,
                   output_path: str):
    """
    Filter data to ward + category, compute growth rates with formula shown.
    Writes per-period CSV output. Flags nulls — never skips or interpolates.
    """
    # Validate ward and category exist in data
    valid_wards = sorted(set(r["ward"] for r in data))
    valid_categories = sorted(set(r["category"] for r in data))

    if ward not in valid_wards:
        print(f"ERROR: Ward '{ward}' not found in data.", file=sys.stderr)
        print(f"Valid wards: {valid_wards}", file=sys.stderr)
        sys.exit(1)

    if category not in valid_categories:
        print(f"ERROR: Category '{category}' not found in data.", file=sys.stderr)
        print(f"Valid categories: {valid_categories}", file=sys.stderr)
        sys.exit(1)

    # Filter to specified ward + category only (Enforcement Rule 1)
    filtered = [r for r in data if r["ward"] == ward and r["category"] == category]
    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    print(f"Computing {growth_type} growth for: {ward} / {category}")
    print(f"Filtered to {len(filtered)} rows.\n")

    # Compute growth
    results = []
    fieldnames = ["period", "ward", "category", "actual_spend", "previous_spend",
                  "growth_pct", "formula", "flag"]

    for i, row in enumerate(filtered):
        period = row["period"]
        actual_raw = row.get("actual_spend", "").strip()
        note = row.get("notes", "").strip()

        result = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": "",
            "previous_spend": "",
            "growth_pct": "",
            "formula": "",
            "flag": ""
        }

        # Handle null actual_spend (Enforcement Rule 2)
        if not actual_raw:
            result["actual_spend"] = "NULL"
            result["growth_pct"] = "NULL"
            result["formula"] = "N/A — actual_spend is null"
            flag_reason = note if note else "No reason given"
            result["flag"] = f"NULL_DATA: {flag_reason}"
            results.append(result)
            continue

        actual = float(actual_raw)
        result["actual_spend"] = f"{actual}"

        if growth_type == "MoM":
            if i == 0:
                result["previous_spend"] = "N/A"
                result["growth_pct"] = "N/A"
                result["formula"] = "N/A — no prior month"
                result["flag"] = "FIRST_PERIOD"
            else:
                prev_raw = filtered[i - 1].get("actual_spend", "").strip()
                if not prev_raw:
                    result["previous_spend"] = "NULL"
                    result["growth_pct"] = "NULL"
                    result["formula"] = "N/A — previous month actual_spend is null"
                    result["flag"] = "PREV_NULL"
                else:
                    prev = float(prev_raw)
                    growth = ((actual - prev) / prev) * 100
                    result["previous_spend"] = f"{prev}"
                    result["growth_pct"] = f"{growth:+.1f}%"
                    result["formula"] = f"(({actual} - {prev}) / {prev}) × 100 = {growth:+.1f}%"

        elif growth_type == "YoY":
            # YoY: compare same month in prior year
            try:
                curr_year, curr_month = map(int, period.split("-"))
                prev_year_period = f"{curr_year - 1:04d}-{curr_month:02d}"
            except ValueError:
                prev_year_period = None

            # Find matching row for same month in previous year
            prev_row = None
            if prev_year_period:
                for r in filtered:
                    if r["period"] == prev_year_period:
                        prev_row = r
                        break

            if not prev_row:
                result["previous_spend"] = "N/A"
                result["growth_pct"] = "N/A"
                result["formula"] = f"N/A — no data for previous year ({prev_year_period})"
                result["flag"] = "NO_PRIOR_YEAR"
            else:
                prev_raw = prev_row.get("actual_spend", "").strip()
                if not prev_raw:
                    result["previous_spend"] = "NULL"
                    result["growth_pct"] = "NULL"
                    result["formula"] = f"N/A — previous year ({prev_year_period}) actual_spend is null"
                    result["flag"] = "PREV_NULL"
                else:
                    prev = float(prev_raw)
                    growth = ((actual - prev) / prev) * 100
                    result["previous_spend"] = f"{prev}"
                    result["growth_pct"] = f"{growth:+.1f}%"
                    result["formula"] = f"(({actual} - {prev}) / {prev}) × 100 = {growth:+.1f}%"


        results.append(result)

    # Write output CSV
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Output written to {output_path} ({len(results)} rows).")

    # Print summary
    null_count = sum(1 for r in results if "NULL" in r.get("growth_pct", ""))
    computed = sum(1 for r in results if r.get("growth_pct", "").endswith("%"))
    print(f"  Computed: {computed} | Null/flagged: {null_count} | "
          f"First period: {1 if growth_type == 'MoM' else 0}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to filter")
    parser.add_argument("--category", required=True, help="Category name to filter")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                        help="Growth calculation type: MoM (month-over-month) or YoY (year-over-year)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Step 1: Load and validate dataset
    data = load_dataset(args.input)

    # Step 2: Compute growth (Enforcement Rule 1: per-ward per-category only)
    compute_growth(data, args.ward, args.category, args.growth_type, args.output)

    print(f"\nDone. Results written to {args.output}")


if __name__ == "__main__":
    main()
