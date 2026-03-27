"""
UC-0C app.py — Number That Looks Right
Built using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

# ── SKILL: load_dataset ──────────────────────────────────────────────────────
def load_dataset(file_path: str) -> list:
    """
    Read ward budget CSV, validate columns, report NULLs before returning.
    Output: list of row dicts; prints NULL report to stdout.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Could not find dataset at '{file_path}'")
        sys.exit(1)

    # Validate required columns
    if not rows:
        print("Error: CSV file is empty.")
        sys.exit(1)

    actual_cols = set(rows[0].keys())
    missing = REQUIRED_COLUMNS - actual_cols
    if missing:
        print(f"Error: Missing required columns: {missing}")
        sys.exit(1)

    # Report NULLs BEFORE returning (enforcement rule 2)
    null_rows = [(r["period"], r["ward"], r["category"], r.get("notes", ""))
                 for r in rows if not r.get("actual_spend", "").strip()]

    print(f"\n=== NULL REPORT: {len(null_rows)} rows with missing actual_spend ===")
    for period, ward, category, note in null_rows:
        print(f"  [{period}] {ward} | {category} — Reason: {note or 'No reason provided'}")
    print("=" * 65 + "\n")

    return rows


# ── SKILL: compute_growth ─────────────────────────────────────────────────────
def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filter to a single ward+category, compute per-period growth with formula shown.
    Enforcement: NULLs flagged, formula shown, no cross-ward aggregation.
    """
    # Enforce valid growth_type (never guess)
    if growth_type not in ("MoM", "YoY"):
        print(f"Error: --growth-type must be 'MoM' or 'YoY'. Got '{growth_type}'. Refusing to proceed.")
        sys.exit(1)

    # Filter to only the specified ward + category (no cross-ward aggregation)
    filtered = [r for r in rows
                if r["ward"].strip() == ward.strip()
                and r["category"].strip() == category.strip()]

    if not filtered:
        print(f"Error: No data found for ward='{ward}' and category='{category}'.")
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        raw_spend = row.get("actual_spend", "").strip()
        notes = row.get("notes", "").strip()

        # NULL handling enforcement
        if not raw_spend:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "previous_spend": "N/A",
                "growth_pct": "N/A",
                "formula": "N/A",
                "null_flag": "TRUE",
                "null_reason": notes or "No reason provided"
            })
            continue

        current = float(raw_spend)

        # Find previous period spend (skip NULLs when looking back)
        if growth_type == "MoM":
            prev_row = filtered[i - 1] if i > 0 else None
            formula_label = "MoM% = (current - previous) / previous * 100"
        else:  # YoY
            # Look back 12 months
            prev_row = next((filtered[j] for j in range(i - 1, -1, -1)
                             if filtered[j]["period"][:4] == str(int(period[:4]) - 1)
                             and filtered[j]["period"][5:] == period[5:]), None)
            formula_label = "YoY% = (current - previous) / previous * 100"

        if prev_row is None or not prev_row.get("actual_spend", "").strip():
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{current:.2f}",
                "previous_spend": "N/A",
                "growth_pct": "N/A (no prior period)",
                "formula": formula_label,
                "null_flag": "FALSE",
                "null_reason": ""
            })
        else:
            previous = float(prev_row["actual_spend"])
            if previous == 0:
                growth_pct = "N/A (prev=0)"
            else:
                growth_pct = f"{((current - previous) / previous * 100):+.1f}%"

            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{current:.2f}",
                "previous_spend": f"{previous:.2f}",
                "growth_pct": growth_pct,
                "formula": formula_label,
                "null_flag": "FALSE",
                "null_reason": ""
            })

    return results


# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Ward name to filter (exact match)")
    parser.add_argument("--category",    required=True,  help="Category to filter (exact match)")
    parser.add_argument("--growth-type", required=True,  help="MoM or YoY")
    parser.add_argument("--output",      required=True,  help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Skill 1: Load and validate dataset, report NULLs first
    all_rows = load_dataset(args.input)

    # Skill 2: Compute growth with formula shown for every row
    results = compute_growth(all_rows, args.ward, args.category, args.growth_type)

    # Write output CSV
    fieldnames = ["period", "ward", "category", "actual_spend", "previous_spend",
                  "growth_pct", "formula", "null_flag", "null_reason"]
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth output written to {args.output} ({len(results)} rows)")


if __name__ == "__main__":
    main()
