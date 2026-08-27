"""
UC-0C Budget Growth Analyser
Implements load_dataset and compute_growth as defined in skills.md.
Enforcement rules drawn directly from agents.md.
"""

import argparse
import csv
import sys
from pathlib import Path

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
OUTPUT_FIELDNAMES = [
    "period", "ward", "category",
    "actual_spend", "prev_period", "prev_spend",
    "growth_pct", "formula_used", "null_flag",
]


# ── Skill: load_dataset ──────────────────────────────────────────────────────

def load_dataset(input_path: str):
    """
    Read CSV, validate columns, report nulls before returning.
    Returns: (rows: list[dict], null_report: list[dict])
    """
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw_rows = list(reader)
        if not raw_rows:
            raise ValueError("Input file is empty.")
        columns = set(reader.fieldnames or [])

    missing = REQUIRED_COLUMNS - columns
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    rows = []
    null_report = []

    for row in raw_rows:
        spend_raw = row.get("actual_spend", "").strip()

        if spend_raw == "":
            # Blank — genuine null
            row["_actual_spend_parsed"] = None
            row["_is_null"] = True
            null_report.append({
                "period":   row["period"],
                "ward":     row["ward"],
                "category": row["category"],
                "reason":   row.get("notes", "No reason provided").strip() or "No reason provided",
            })
        else:
            try:
                row["_actual_spend_parsed"] = float(spend_raw)
                row["_is_null"] = False
            except ValueError:
                row["_actual_spend_parsed"] = None
                row["_is_null"] = True
                null_report.append({
                    "period":   row["period"],
                    "ward":     row["ward"],
                    "category": row["category"],
                    "reason":   f"Non-numeric value: '{spend_raw}'",
                })

        rows.append(row)

    # ── Null report printed before any computation (agents.md rule 2) ────────
    print(f"\n{'='*60}")
    print(f"DATASET LOADED: {len(rows)} rows")
    print(f"NULL actual_spend rows detected: {len(null_report)}")
    if null_report:
        print()
        for n in null_report:
            print(f"  ⚠  {n['period']} | {n['ward']} | {n['category']}")
            print(f"     Reason: {n['reason']}")
    print(f"{'='*60}\n")

    return rows, null_report


# ── Skill: compute_growth ────────────────────────────────────────────────────

def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filter to one ward + category, compute per-period growth.
    Returns list of result dicts with formula shown for every row.
    """
    # Enforcement: growth_type must be specified exactly
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            f"Invalid growth_type '{growth_type}'. "
            f"Must be exactly 'MoM' or 'YoY'. Will not guess."
        )

    # Filter to the requested ward + category
    filtered = [
        r for r in rows
        if r["ward"].strip() == ward.strip()
        and r["category"].strip() == category.strip()
    ]

    if not filtered:
        raise ValueError(
            f"No rows found for ward='{ward}' and category='{category}'. "
            f"Check spelling — ward and category must match the CSV exactly."
        )

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    # Build a lookup: period → parsed spend (None if null)
    spend_by_period = {r["period"]: r["_actual_spend_parsed"] for r in filtered}

    results = []

    for row in filtered:
        period = row["period"]
        current_spend = row["_actual_spend_parsed"]
        is_null = row["_is_null"]

        # Determine previous period
        if growth_type == "MoM":
            year, month = int(period[:4]), int(period[5:])
            if month == 1:
                prev_period = f"{year-1}-12"
            else:
                prev_period = f"{year}-{month-1:02d}"
        else:  # YoY
            year, month = int(period[:4]), int(period[5:])
            prev_period = f"{year-1}-{month:02d}"

        prev_spend = spend_by_period.get(prev_period)  # None if not in dataset or null

        # Determine null_flag and compute growth
        if is_null:
            null_flag = "NULL"
            growth_pct = None
            formula_used = "NOT_COMPUTED — current period is null"
        elif prev_spend is None:
            null_flag = "PREV_NULL"
            growth_pct = None
            if prev_period not in spend_by_period:
                formula_used = f"NOT_COMPUTED — {prev_period} not in dataset"
            else:
                formula_used = f"NOT_COMPUTED — {prev_period} is null"
        else:
            null_flag = ""
            growth_pct = round((current_spend - prev_spend) / prev_spend * 100, 1)
            formula_used = f"({current_spend} - {prev_spend}) / {prev_spend}"

        results.append({
            "period":       period,
            "ward":         ward,
            "category":     category,
            "actual_spend": "" if is_null else current_spend,
            "prev_period":  prev_period,
            "prev_spend":   "" if prev_spend is None else prev_spend,
            "growth_pct":   "" if growth_pct is None else f"{growth_pct:+.1f}%",
            "formula_used": formula_used,
            "null_flag":    null_flag,
        })

    return results


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyser")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Exact ward name")
    parser.add_argument("--category",    required=True,  help="Exact category name")
    parser.add_argument("--growth-type", required=False, default=None,
                        dest="growth_type",
                        help="MoM or YoY — REQUIRED, will not be guessed")
    parser.add_argument("--output",      required=True,  help="Path to write results CSV")
    args = parser.parse_args()

    # Enforcement: refuse if growth-type not given (agents.md rule 4)
    if args.growth_type is None:
        print(
            "ERROR: --growth-type is required. Please specify 'MoM' or 'YoY'.\n"
            "This tool will not guess a growth formula — specify it explicitly.",
            file=sys.stderr
        )
        sys.exit(1)

    if args.growth_type not in ("MoM", "YoY"):
        print(
            f"ERROR: --growth-type must be 'MoM' or 'YoY', got '{args.growth_type}'.",
            file=sys.stderr
        )
        sys.exit(1)

    # Load and validate
    try:
        rows, null_report = load_dataset(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Compute growth
    try:
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDNAMES)
        writer.writeheader()
        writer.writerows(results)

    # Print summary table to terminal
    print(f"Growth Analysis: {args.ward} | {args.category} | {args.growth_type}\n")
    print(f"{'Period':<10} {'Actual':>8} {'Prev':>8} {'Growth':>9}  {'Flag':<12} Formula")
    print("-" * 75)
    for r in results:
        flag = r["null_flag"] or ""
        spend = f"{r['actual_spend']}" if r["actual_spend"] != "" else "NULL"
        prev  = f"{r['prev_spend']}"   if r["prev_spend"]   != "" else "NULL"
        growth = r["growth_pct"] or "—"
        print(
            f"{r['period']:<10} {spend:>8} {prev:>8} {growth:>9}  {flag:<12} {r['formula_used']}"
        )

    # Reference value check
    ref_checks = [
        ("2024-07", "Ward 1 – Kasba", "Roads & Pothole Repair", "+33.1%"),
        ("2024-10", "Ward 1 – Kasba", "Roads & Pothole Repair", "-34.8%"),
    ]
    if args.ward == "Ward 1 – Kasba" and args.category == "Roads & Pothole Repair":
        print("\n── Reference value check ──")
        result_by_period = {r["period"]: r for r in results}
        for period, w, c, expected in ref_checks:
            actual_growth = result_by_period.get(period, {}).get("growth_pct", "NOT FOUND")
            status = "✓" if actual_growth == expected else f"✗ (got {actual_growth})"
            print(f"  {period} MoM growth — expected {expected}: {status}")

    null_count = sum(1 for r in results if r["null_flag"])
    print(f"\nSummary: {len(results)} periods | {null_count} flagged (null or prev null)")
    print(f"Results written to {args.output}")


if __name__ == "__main__":
    main()