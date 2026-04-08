"""
UC-0C — Number That Looks Right
Built using the RICE → agents.md → skills.md → CRAFT workflow.

Role: Budget Growth Analyst — per-ward, per-category, never aggregated.
Intent: Per-period growth table with formula shown, nulls flagged.
Context: ward_budget.csv only; actual_spend only (not budgeted_amount).
Enforcement: No cross-ward aggregation; flag nulls; show formula; refuse if growth-type missing.
"""
import argparse
import csv
import sys


# ── Skill: load_dataset ──────────────────────────────────────────────────────

def load_dataset(input_path: str) -> dict:
    """
    Read ward_budget.csv, validate columns, report null actual_spend rows.
    Returns structured data with null report upfront.
    """
    try:
        with open(input_path, "r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not read input CSV: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required columns
    required = {"period", "ward", "category", "budgeted_amount", "actual_spend"}
    if rows:
        found = set(rows[0].keys())
        missing = required - found
        if missing:
            print(f"ERROR: Missing required columns: {missing}", file=sys.stderr)
            sys.exit(1)

    # Build null report
    null_report = []
    wards = set()
    categories = set()

    for row in rows:
        wards.add(row["ward"])
        categories.add(row["category"])
        if not row["actual_spend"].strip():
            null_report.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "reason": row.get("notes", "No reason provided").strip()
            })

    # Print null report upfront
    print(f"Loaded {len(rows)} rows. Found {len(null_report)} null actual_spend values:")
    for nr in null_report:
        print(f"  ⚠ {nr['period']} · {nr['ward']} · {nr['category']} — {nr['reason']}")

    return {
        "data": rows,
        "columns": list(rows[0].keys()) if rows else [],
        "total_rows": len(rows),
        "null_report": null_report,
        "null_count": len(null_report),
        "wards": sorted(wards),
        "categories": sorted(categories),
    }


# ── Skill: compute_growth ────────────────────────────────────────────────────

def compute_growth(data: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    """
    Filter to ward + category, compute per-period growth with formula shown.
    Flags null periods and the period immediately after a null.
    """
    # Validate growth_type
    if growth_type not in ("MoM", "YoY"):
        print(f"ERROR: Invalid growth-type '{growth_type}'. Must be 'MoM' or 'YoY'.", file=sys.stderr)
        sys.exit(1)

    # Filter data
    filtered = [r for r in data if r["ward"] == ward and r["category"] == category]
    if not filtered:
        all_wards = sorted(set(r["ward"] for r in data))
        all_cats = sorted(set(r["category"] for r in data))
        print(f"ERROR: No data found for ward='{ward}', category='{category}'.", file=sys.stderr)
        print(f"  Valid wards: {all_wards}", file=sys.stderr)
        print(f"  Valid categories: {all_cats}", file=sys.stderr)
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    # Parse actual_spend values
    periods = []
    for row in filtered:
        spend_str = row["actual_spend"].strip()
        spend = float(spend_str) if spend_str else None
        periods.append({
            "period": row["period"],
            "actual_spend": spend,
            "null_reason": row.get("notes", "").strip() if spend is None else "",
        })

    # Compute growth
    results = []
    for i, current in enumerate(periods):
        result = {
            "period": current["period"],
            "actual_spend": current["actual_spend"] if current["actual_spend"] is not None else "NULL",
            "previous_spend": "N/A",
            "growth_pct": "N/A",
            "formula": "N/A — first period",
            "null_reason": current["null_reason"],
        }

        if growth_type == "MoM" and i > 0:
            prev = periods[i - 1]
            prev_spend = prev["actual_spend"]
            curr_spend = current["actual_spend"]

            result["previous_spend"] = prev_spend if prev_spend is not None else "NULL"

            if curr_spend is None:
                result["growth_pct"] = "NULL"
                result["formula"] = f"NULL — actual_spend missing ({current['null_reason']})"
            elif prev_spend is None:
                result["growth_pct"] = "NULL"
                result["formula"] = f"NULL — previous period actual_spend missing"
            elif prev_spend == 0:
                result["growth_pct"] = "N/A"
                result["formula"] = "N/A — division by zero (previous spend is 0)"
            else:
                growth = ((curr_spend - prev_spend) / prev_spend) * 100
                sign = "+" if growth >= 0 else ""
                result["growth_pct"] = round(growth, 1)
                result["formula"] = (
                    f"(({curr_spend} - {prev_spend}) / {prev_spend}) × 100 "
                    f"= {sign}{round(growth, 1)}%"
                )

        elif growth_type == "YoY":
            # YoY: compare same month, previous year
            # Since data is only 2024, YoY is not computable
            result["growth_pct"] = "N/A"
            result["formula"] = "N/A — only 2024 data available, no prior year for YoY"

        results.append(result)

    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyser")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Budget category (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                        help="Growth calculation type: MoM (month-over-month) or YoY (year-over-year)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    # Step 1: Load and validate dataset
    dataset = load_dataset(args.input)

    # Step 2: Compute growth
    print(f"\nComputing {args.growth_type} growth for: {args.ward} / {args.category}")
    results = compute_growth(dataset["data"], args.ward, args.category, args.growth_type)

    # Step 3: Write output CSV
    fieldnames = ["period", "actual_spend", "previous_spend", "growth_pct", "formula", "null_reason"]
    try:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"ERROR: Could not write output: {e}", file=sys.stderr)
        sys.exit(1)

    # Print summary
    null_periods = [r for r in results if r["actual_spend"] == "NULL"]
    computed = [r for r in results if isinstance(r["growth_pct"], (int, float))]
    print(f"\nResults: {len(results)} periods, {len(computed)} growth values computed, {len(null_periods)} null periods flagged.")
    print(f"Done. Output written to {args.output}")


if __name__ == "__main__":
    main()
