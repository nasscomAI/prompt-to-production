"""
UC-0C — Number That Looks Right
Implements agents.md + skills.md: load_dataset and compute_growth.
Per-ward per-category budget growth with formula shown and null rows flagged.
"""
import argparse
import csv
import sys

# ── Skill 1: load_dataset ───────────────────────────────────────────────────

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

def load_dataset(file_path: str) -> dict:
    """
    Read ward_budget.csv, validate columns, and identify null actual_spend rows.

    Returns: {"rows": [...], "null_report": [...]}
    Raises FileNotFoundError or ValueError on bad input.
    """
    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            raw_rows = list(reader)
            columns  = set(reader.fieldnames or [])
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    missing = REQUIRED_COLUMNS - columns
    if missing:
        raise ValueError(f"Missing columns in dataset: {', '.join(sorted(missing))}")

    null_report = []
    rows = []
    for row in raw_rows:
        spend = row.get("actual_spend", "").strip()
        if spend == "" or spend is None:
            null_report.append({
                "period":   row["period"],
                "ward":     row["ward"],
                "category": row["category"],
                "notes":    row.get("notes", ""),
            })
        rows.append(row)

    return {"rows": rows, "null_report": null_report}


# ── Skill 2: compute_growth ──────────────────────────────────────────────────

def compute_growth(rows: list[dict], ward: str, category: str,
                   growth_type: str) -> list[dict]:
    """
    Filter to one ward+category, compute MoM or YoY growth per period.

    Returns list of dicts: period, actual_spend, prior_value, formula, growth_pct.
    Raises ValueError on invalid inputs.
    """
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            f"growth_type must be 'MoM' or 'YoY'. Received: {growth_type!r}."
        )

    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not filtered:
        raise ValueError(
            f"Ward '{ward}' / Category '{category}' not found in dataset. "
            "Check spelling and case."
        )

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    def parse_spend(r):
        v = r.get("actual_spend", "").strip()
        if v == "":
            return None
        try:
            return float(v)
        except ValueError:
            return None

    # Build lookup: period → spend value
    period_to_spend = {}
    for r in filtered:
        period_to_spend[r["period"]] = parse_spend(r)

    results = []
    for r in filtered:
        period  = r["period"]
        spend   = parse_spend(r)
        notes   = r.get("notes", "")

        # Determine prior period key
        if growth_type == "MoM":
            year, month = int(period[:4]), int(period[5:])
            month -= 1
            if month == 0:
                month, year = 12, year - 1
            prior_key = f"{year:04d}-{month:02d}"
        else:  # YoY
            year = int(period[:4]) - 1
            prior_key = f"{year:04d}-{period[5:]}"

        prior_spend = period_to_spend.get(prior_key)

        # Null current row
        if spend is None:
            results.append({
                "period":       period,
                "actual_spend": "NULL",
                "prior_value":  prior_spend if prior_spend is not None else "NULL",
                "formula":      "N/A — null row",
                "growth_pct":   f"NULL_GROWTH: {notes}" if notes else "NULL_GROWTH: no actual_spend",
            })
            continue

        # No prior period available
        if prior_spend is None:
            results.append({
                "period":       period,
                "actual_spend": spend,
                "prior_value":  "NULL",
                "formula":      "N/A — no prior period",
                "growth_pct":   "NULL_GROWTH: no prior period available",
            })
            continue

        # Prior is null
        if prior_spend == 0:
            results.append({
                "period":       period,
                "actual_spend": spend,
                "prior_value":  prior_spend,
                "formula":      f"({spend} - {prior_spend}) / {prior_spend} × 100",
                "growth_pct":   "NULL_GROWTH: prior period spend is zero (division undefined)",
            })
            continue

        growth = round((spend - prior_spend) / prior_spend * 100, 1)
        results.append({
            "period":       period,
            "actual_spend": spend,
            "prior_value":  prior_spend,
            "formula":      f"({spend} - {prior_spend}) / {prior_spend} × 100",
            "growth_pct":   growth,
        })

    return results


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Exact ward name")
    parser.add_argument("--category",    required=True,  help="Exact category name")
    parser.add_argument("--growth-type", required=True,  help="MoM or YoY",
                        dest="growth_type")
    parser.add_argument("--output",      required=True,  help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Skill 1: load + validate
    try:
        dataset = load_dataset(args.input)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    # Print null report before any computation
    if dataset["null_report"]:
        print(f"\nWARNING: NULL ROWS DETECTED ({len(dataset['null_report'])}) -- these will not be computed:")
        for nr in dataset["null_report"]:
            print(f"   {nr['period']} | {nr['ward']} | {nr['category']} | notes: {nr['notes']}")
        print()

    # Skill 2: compute growth
    try:
        results = compute_growth(
            dataset["rows"], args.ward, args.category, args.growth_type
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    # Write output CSV
    fields = ["period", "actual_spend", "prior_value", "formula", "growth_pct"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth table written to {args.output}  ({len(results)} periods)")


if __name__ == "__main__":
    main()
