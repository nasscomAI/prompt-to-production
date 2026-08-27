"""
UC-0C app.py — Budget Growth Analyser
Implements skills: load_dataset + compute_growth
Enforcement from agents.md (RICE):
  - Per-ward per-category only — refuses all-ward aggregation
  - Null rows flagged before computation, never imputed
  - Formula shown on every output row
  - growth-type must be explicit — never guessed
"""
import argparse
import csv
import sys
from typing import Optional


# ── Skill: load_dataset ───────────────────────────────────────────────────────

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(file_path: str) -> dict:
    """
    Load ward_budget.csv, validate columns, report null actual_spend rows.
    Returns { rows, null_rows, null_count } or raises on failure.
    """
    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValueError("File appears empty or has no header row.")
            missing = REQUIRED_COLUMNS - set(reader.fieldnames)
            if missing:
                raise ValueError(f"Missing required columns: {missing}")
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"LOAD_FAILED: '{file_path}' not found.")
    except OSError as e:
        raise OSError(f"LOAD_FAILED: {e}")

    null_rows = [
        r for r in rows if r.get("actual_spend", "").strip() == ""
    ]

    return {
        "rows":       rows,
        "null_rows":  null_rows,
        "null_count": len(null_rows),
    }


# ── Skill: compute_growth ─────────────────────────────────────────────────────

def _parse_spend(value: str) -> Optional[float]:
    v = value.strip()
    if v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def compute_growth(rows: list, growth_type: str, ward: str, category: str) -> list:
    """
    Compute per-period MoM or YoY growth for a single ward+category.
    Returns a list of result dicts with formula and null flags.
    """
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            f"growth_type must be 'MoM' or 'YoY' — received: '{growth_type}'"
        )

    # Scope validation: only one ward + category allowed
    wards_found = {r["ward"] for r in rows}
    cats_found  = {r["category"] for r in rows}
    if len(wards_found) > 1 or len(cats_found) > 1:
        raise ValueError(
            "compute_growth received mixed ward/category data — scope violation."
        )

    # Sort by period
    sorted_rows = sorted(rows, key=lambda r: r["period"])

    # Build lookup: period → actual_spend + notes
    period_data: dict[str, dict] = {
        r["period"]: {
            "spend": _parse_spend(r["actual_spend"]),
            "notes": r.get("notes", "").strip(),
        }
        for r in sorted_rows
    }

    results = []
    for r in sorted_rows:
        period = r["period"]
        actual = _parse_spend(r["actual_spend"])
        notes  = r.get("notes", "").strip()

        # Determine prior period
        if growth_type == "MoM":
            year, month = int(period[:4]), int(period[5:7])
            if month == 1:
                prior_period = f"{year - 1}-12"
            else:
                prior_period = f"{year}-{month - 1:02d}"
        else:  # YoY
            year = int(period[:4])
            prior_period = f"{year - 1}-{period[5:]}"

        prior_entry = period_data.get(prior_period)
        prior = prior_entry["spend"] if prior_entry else None

        # Null handling — never compute from null
        if actual is None:
            growth_pct = "NULL_FLAGGED"
            null_reason = notes if notes else "actual_spend is null"
            formula = "N/A — actual_spend is null"
        elif prior is None:
            growth_pct = "NULL_FLAGGED"
            null_reason = f"prior period {prior_period} not available or null"
            formula = f"N/A — prior period {prior_period} unavailable"
        else:
            if prior == 0:
                growth_pct = "NULL_FLAGGED"
                null_reason = f"prior period {prior_period} spend is zero — division undefined"
                formula = f"({actual} - {prior}) / {prior} × 100 = undefined"
            else:
                pct = round((actual - prior) / prior * 100, 1)
                sign = "+" if pct >= 0 else ""
                growth_pct = pct
                null_reason = ""
                formula = f"({actual} - {prior}) / {prior} × 100 = {sign}{pct}%"

        results.append({
            "period":       period,
            "ward":         ward,
            "category":     category,
            "actual_spend": actual if actual is not None else "NULL",
            "prior_spend":  prior if prior is not None else "NULL",
            "growth_pct":   growth_pct,
            "formula":      formula,
            "null_reason":  null_reason,
        })

    return results


# ── Entry point ───────────────────────────────────────────────────────────────

OUTPUT_FIELDS = [
    "period", "ward", "category", "actual_spend",
    "prior_spend", "growth_pct", "formula", "null_reason",
]


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyser")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Ward name (exact string)")
    parser.add_argument("--category",    required=True,  help="Category name (exact string)")
    parser.add_argument("--growth-type", required=False, dest="growth_type",
                        help="MoM or YoY")
    parser.add_argument("--output",      required=True,  help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforcement: growth-type must be explicit
    if not args.growth_type:
        print(
            "ERROR: Growth type not specified. "
            "Please provide --growth-type MoM or --growth-type YoY.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Skill 1: load_dataset
    try:
        dataset = load_dataset(args.input)
    except (FileNotFoundError, OSError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(dataset['rows'])} rows. "
          f"Null actual_spend rows: {dataset['null_count']}")
    for nr in dataset["null_rows"]:
        print(f"  NULL: {nr['period']} · {nr['ward']} · {nr['category']} — {nr.get('notes','')}")

    # Filter to requested ward + category
    filtered = [
        r for r in dataset["rows"]
        if r["ward"] == args.ward and r["category"] == args.category
    ]

    if not filtered:
        print(
            f"ERROR: No rows found for ward='{args.ward}' category='{args.category}'. "
            "Check exact spelling.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Skill 2: compute_growth
    try:
        results = compute_growth(filtered, args.growth_type, args.ward, args.category)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Write output
    try:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()
            writer.writerows(results)
    except OSError as e:
        print(f"ERROR: Could not write output: {e}", file=sys.stderr)
        sys.exit(1)

    null_flagged = sum(1 for r in results if r["growth_pct"] == "NULL_FLAGGED")
    print(f"Done. {len(results)} periods written to '{args.output}'. "
          f"NULL_FLAGGED: {null_flagged}.")


if __name__ == "__main__":
    main()
