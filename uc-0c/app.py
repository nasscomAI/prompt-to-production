"""
UC-0C — Number That Looks Right: Budget Growth Calculator
Built using RICE → agents.md → skills.md → CRAFT workflow.

Enforcement (from agents.md):
1. Never aggregate across wards or categories — refuse if asked
2. Report ALL null actual_spend rows before any computation
3. Show formula column in every output row
4. Refuse if --growth-type not specified — never silently default
5. NULL rows appear in output as NULL_FLAGGED — never skipped

CRAFT fix applied:
- Silent aggregation: naive prompt returned one number across all wards → enforced per-ward per-category only
- Null skipping: naive prompt ignored 5 null rows → added load_dataset null report
- Formula assumption: naive prompt silently chose MoM → added explicit refusal if growth-type missing
"""
import argparse
import csv
import sys


# ─── Skill: load_dataset ──────────────────────────────────────────────────────

def load_dataset(file_path: str):
    """
    Read ward_budget.csv, validate columns, report null actual_spend rows.
    Returns (data, null_report).
    """
    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

    try:
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            actual_cols = set(reader.fieldnames or [])
    except FileNotFoundError:
        print(f"ERROR: Dataset file not found: {file_path}", file=sys.stderr)
        raise

    missing_cols = required_columns - actual_cols
    if missing_cols:
        raise ValueError(f"Missing required columns: {sorted(missing_cols)}")

    null_report = []
    data = []

    for row in rows:
        actual_spend_raw = row.get("actual_spend", "").strip()
        if actual_spend_raw == "" or actual_spend_raw is None:
            null_report.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": row["budgeted_amount"],
                "reason": row.get("notes", "No reason given") or "No reason given"
            })
        data.append(row)

    # Always print null report before returning — enforcement rule 2
    print(f"\n{'='*60}")
    print(f"NULL REPORT — {len(null_report)} null actual_spend rows found:")
    print(f"{'='*60}")
    if null_report:
        for nr in null_report:
            print(f"  ⚠  {nr['period']} | {nr['ward']} | {nr['category']}")
            print(f"     Reason: {nr['reason']}")
    else:
        print("  None — all actual_spend values are present.")
    print(f"{'='*60}\n")

    return data, null_report


# ─── Skill: compute_growth ────────────────────────────────────────────────────

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Compute per-period growth for ONE ward + ONE category.
    Refuses cross-ward/category aggregation.
    Shows formula in every output row.
    Flags null rows as NULL_FLAGGED.
    """
    # Validate growth_type (enforcement rule 4)
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            f"Invalid growth type: '{growth_type}'. "
            "Please provide --growth-type MoM or --growth-type YoY."
        )

    # Filter to exact ward + category (enforcement rule 1)
    filtered = [
        r for r in data
        if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip()
    ]

    if not filtered:
        available_wards = sorted(set(r["ward"] for r in data))
        available_cats = sorted(set(r["category"] for r in data))
        raise ValueError(
            f"No data found for ward='{ward}', category='{category}'.\n"
            f"Available wards: {available_wards}\n"
            f"Available categories: {available_cats}"
        )

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    results = []

    for i, row in enumerate(filtered):
        period = row["period"]
        actual_raw = row.get("actual_spend", "").strip()

        # Handle null (enforcement rule 5 — null rows must appear as NULL_FLAGGED)
        if actual_raw == "":
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "previous_value": "N/A",
                "growth_pct": "NULL_FLAGGED",
                "formula": "N/A (null period — see null report above)"
            })
            continue

        try:
            current = float(actual_raw)
        except ValueError:
            results.append({
                "period": period,
                "actual_spend": actual_raw,
                "previous_value": "N/A",
                "growth_pct": "NULL_FLAGGED",
                "formula": f"N/A (invalid value '{actual_raw}')"
            })
            continue

        # Find the comparison period
        if growth_type == "MoM":
            if i == 0:
                results.append({
                    "period": period,
                    "actual_spend": f"{current:.1f}",
                    "previous_value": "N/A",
                    "growth_pct": "N/A",
                    "formula": "N/A (first period — no prior month value)"
                })
                continue
            # Find previous period — walk backwards to find non-null
            prev_row = None
            for j in range(i - 1, -1, -1):
                prev_raw = filtered[j].get("actual_spend", "").strip()
                if prev_raw != "":
                    try:
                        prev_val = float(prev_raw)
                        prev_row = (filtered[j]["period"], prev_val)
                    except ValueError:
                        pass
                    break

            if prev_row is None:
                results.append({
                    "period": period,
                    "actual_spend": f"{current:.1f}",
                    "previous_value": "NULL (prior period is null)",
                    "growth_pct": "NULL_FLAGGED",
                    "formula": "N/A (prior period is null — cannot compute MoM)"
                })
                continue

            prev_period, prev_val = prev_row
            growth = ((current - prev_val) / prev_val) * 100
            formula_str = f"(({current:.1f} - {prev_val:.1f}) / {prev_val:.1f}) * 100"

            results.append({
                "period": period,
                "actual_spend": f"{current:.1f}",
                "previous_value": f"{prev_val:.1f} ({prev_period})",
                "growth_pct": f"{growth:+.1f}%",
                "formula": formula_str
            })

        elif growth_type == "YoY":
            # Find same month in prior year
            parts = period.split("-")
            if len(parts) != 2:
                results.append({
                    "period": period,
                    "actual_spend": f"{current:.1f}",
                    "previous_value": "N/A",
                    "growth_pct": "N/A",
                    "formula": "N/A (cannot parse period for YoY)"
                })
                continue

            year, month = parts
            prior_year_period = f"{int(year)-1}-{month}"
            prior_row = next(
                (r for r in filtered if r["period"] == prior_year_period), None
            )

            if prior_row is None:
                results.append({
                    "period": period,
                    "actual_spend": f"{current:.1f}",
                    "previous_value": "N/A",
                    "growth_pct": "N/A",
                    "formula": f"N/A (no prior year data for {prior_year_period})"
                })
                continue

            prior_raw = prior_row.get("actual_spend", "").strip()
            if prior_raw == "":
                results.append({
                    "period": period,
                    "actual_spend": f"{current:.1f}",
                    "previous_value": f"NULL ({prior_year_period})",
                    "growth_pct": "NULL_FLAGGED",
                    "formula": f"N/A (prior year period {prior_year_period} is null)"
                })
                continue

            prior_val = float(prior_raw)
            growth = ((current - prior_val) / prior_val) * 100
            formula_str = f"(({current:.1f} - {prior_val:.1f}) / {prior_val:.1f}) * 100"

            results.append({
                "period": period,
                "actual_spend": f"{current:.1f}",
                "previous_value": f"{prior_val:.1f} ({prior_year_period})",
                "growth_pct": f"{growth:+.1f}%",
                "formula": formula_str
            })

    return results


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Calculator — per-ward per-category only"
    )
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=False, default=None, help="Exact ward name (required)")
    parser.add_argument("--category",    required=False, default=None, help="Exact category name (required)")
    parser.add_argument("--growth-type", required=False, default=None,
                        dest="growth_type", help="MoM or YoY (required)")
    parser.add_argument("--output",      required=True,  help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforce that ward and category must be provided (enforcement rule 1)
    if not args.ward or not args.category:
        print(
            "ERROR: --ward and --category are required.\n"
            "Aggregation across wards or categories is not permitted.\n"
            "Please specify a single ward and category.",
            file=sys.stderr
        )
        sys.exit(1)

    # Enforce that growth-type must be specified (enforcement rule 4)
    if not args.growth_type:
        print(
            "ERROR: Growth type not specified.\n"
            "Please provide --growth-type MoM or --growth-type YoY.\n"
            "The system will not silently default to either.",
            file=sys.stderr
        )
        sys.exit(1)

    # Load dataset (skill 1 — always prints null report)
    data, null_report = load_dataset(args.input)

    print(f"Computing {args.growth_type} growth for:")
    print(f"  Ward:     {args.ward}")
    print(f"  Category: {args.category}")
    print()

    # Compute growth (skill 2)
    try:
        results = compute_growth(data, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Write output CSV
    fieldnames = ["period", "actual_spend", "previous_value", "growth_pct", "formula"]
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Print results to console
    print(f"{'Period':<12} {'Actual Spend':>14} {'Previous':>16} {'Growth %':>12} {'Formula'}")
    print("-" * 100)
    for r in results:
        print(
            f"{r['period']:<12} {r['actual_spend']:>14} {r['previous_value']:>16} "
            f"{r['growth_pct']:>12} | {r['formula']}"
        )

    print(f"\nDone. Growth output written to {args.output}")
    if null_report:
        print(f"NOTE: {len(null_report)} null rows were flagged in the null report above and appear as NULL_FLAGGED in output.")


if __name__ == "__main__":
    main()
