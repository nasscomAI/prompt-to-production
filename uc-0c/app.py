"""
UC-0C — Budget Growth Calculator: Number That Looks Right
Built using the RICE → agents.md → skills.md → CRAFT workflow.

Agent Role (agents.md):
  Municipal budget analytics agent. Operates at per-ward per-category level only.
  Reports nulls, shows formulas, refuses to aggregate or guess growth type.

Skills (skills.md):
  - load_dataset  : reads CSV, validates columns, reports null inventory before returning
  - compute_growth: filters to ward+category+growth_type, returns per-period table
                    with formula shown and NULL_FLAGGED for null rows

Enforcement (agents.md / README.md):
  1. Never aggregate across wards/categories — refuse if asked.
  2. Flag every null row before computing — report null reason from notes column.
  3. Show formula used in every output row alongside the result.
  4. If --growth-type not specified — refuse and ask, never guess.
"""

import argparse
import csv
import sys
from typing import Dict, List, Optional, Tuple

# ── Allowed growth types ──────────────────────────────────────────────────────
ALLOWED_GROWTH_TYPES = ("MoM", "YoY")

# Required CSV columns (agents.md / skills.md)
REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


# ── Skill: load_dataset ───────────────────────────────────────────────────────

def load_dataset(file_path: str) -> Dict:
    """
    Skill: load_dataset (skills.md)
    Reads ward_budget CSV, validates columns, reports null inventory, returns data.

    Returns:
        {
            "rows":  [list of all row dicts],
            "nulls": [list of null actual_spend rows with null_reason]
        }

    Errors (skills.md):
      - File not found         → FileNotFoundError
      - Missing columns        → ValueError listing missing columns
      - Empty file             → ValueError
      - Never return partial data silently
    """
    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = set(reader.fieldnames or [])
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset file not found: '{file_path}'")
    except (PermissionError, OSError) as exc:
        raise FileNotFoundError(f"Cannot read dataset file '{file_path}': {exc}")

    if not rows:
        raise ValueError(f"Dataset file is empty: '{file_path}'")

    # Validate required columns
    missing_cols = REQUIRED_COLUMNS - fieldnames
    if missing_cols:
        raise ValueError(
            f"Dataset is missing required columns: {sorted(missing_cols)}\n"
            f"Found columns: {sorted(fieldnames)}"
        )

    # Identify and report null actual_spend rows (enforcement rule 2)
    null_rows = []
    for row in rows:
        raw_spend = row.get("actual_spend", "").strip()
        if raw_spend == "" or raw_spend is None:
            null_rows.append({
                "period":          row["period"].strip(),
                "ward":            row["ward"].strip(),
                "category":        row["category"].strip(),
                "budgeted_amount": row["budgeted_amount"].strip(),
                "null_reason":     row.get("notes", "").strip() or "No reason recorded",
            })

    # Print null inventory to stdout (enforcement rule 2 — report before computing)
    print(f"\n[NULL INVENTORY] {len(null_rows)} null actual_spend row(s) found:")
    if null_rows:
        for nr in null_rows:
            print(f"  ⚠  {nr['period']} | {nr['ward']} | {nr['category']} "
                  f"| Reason: {nr['null_reason']}")
    else:
        print("  (none)")
    print()

    return {"rows": rows, "nulls": null_rows}


# ── Skill: compute_growth ────────────────────────────────────────────────────

def compute_growth(
    ward: str,
    category: str,
    growth_type: str,
    dataset: Dict,
) -> List[Dict]:
    """
    Skill: compute_growth (skills.md)
    Filters dataset to ward+category, computes per-period growth with formula shown.

    Returns:
        List of dicts per period:
        {
            "period":       "2024-07",
            "actual_spend": 19.7 | None,
            "growth_pct":   33.1  | None,
            "formula_shown":"(19.7 - 14.8) / 14.8 * 100",
            "null_reason":  "" | "reason string",
            "status":       "OK" | "NULL_FLAGGED" | "FIRST_PERIOD"
        }

    Errors (skills.md):
      - growth_type not in ALLOWED_GROWTH_TYPES → ValueError (never default)
      - ward/category not found                 → ValueError listing available values
      - null in current or previous period      → NULL_FLAGGED, never compute
    """
    # Enforcement rule 4: refuse if growth_type not explicitly specified
    if growth_type not in ALLOWED_GROWTH_TYPES:
        raise ValueError(
            f"[REFUSAL] growth_type '{growth_type}' is not valid.\n"
            f"You must explicitly specify one of: {ALLOWED_GROWTH_TYPES}.\n"
            f"This system will never choose a growth type on your behalf."
        )

    rows = dataset["rows"]
    null_set = {
        (nr["period"], nr["ward"], nr["category"])
        for nr in dataset["nulls"]
    }
    null_reason_map = {
        (nr["period"], nr["ward"], nr["category"]): nr["null_reason"]
        for nr in dataset["nulls"]
    }

    # Filter to the specified ward + category
    filtered = [
        r for r in rows
        if r["ward"].strip() == ward and r["category"].strip() == category
    ]

    if not filtered:
        available_wards = sorted({r["ward"].strip() for r in rows})
        available_cats  = sorted({r["category"].strip() for r in rows})
        raise ValueError(
            f"No data found for ward='{ward}', category='{category}'.\n"
            f"Available wards:      {available_wards}\n"
            f"Available categories: {available_cats}"
        )

    # Sort by period (YYYY-MM strings sort correctly lexicographically)
    filtered.sort(key=lambda r: r["period"].strip())

    # Build a lookup: period → actual_spend (float or None)
    def parse_spend(r: Dict) -> Optional[float]:
        val = r.get("actual_spend", "").strip()
        if val == "":
            return None
        try:
            return float(val)
        except ValueError:
            return None

    period_spend: Dict[str, Optional[float]] = {
        r["period"].strip(): parse_spend(r) for r in filtered
    }
    periods = [r["period"].strip() for r in filtered]

    results = []

    for i, period in enumerate(periods):
        current_spend = period_spend[period]
        current_null  = (period, ward, category) in null_set
        null_reason   = null_reason_map.get((period, ward, category), "")

        # Determine previous period based on growth type
        if growth_type == "MoM":
            prev_period = _previous_month(period)
        else:  # YoY
            prev_period = _previous_year(period)

        prev_spend = period_spend.get(prev_period)  # None if period not in data
        prev_null  = (prev_period, ward, category) in null_set

        # FIRST_PERIOD: no previous period in the filtered data
        if prev_period not in period_spend:
            results.append({
                "period":        period,
                "actual_spend":  current_spend,
                "growth_pct":    None,
                "formula_shown": f"No prior period ({prev_period} not in dataset)",
                "null_reason":   null_reason if current_null else "",
                "status":        "NULL_FLAGGED" if current_null else "FIRST_PERIOD",
            })
            continue

        # NULL_FLAGGED: current or previous period is null (enforcement rule 2)
        if current_null or prev_null:
            flagged_period = period if current_null else prev_period
            flagged_reason = null_reason if current_null else null_reason_map.get(
                (prev_period, ward, category), "null in previous period"
            )
            formula_str = (
                f"Cannot compute — actual_spend is NULL for "
                f"{flagged_period} | Reason: {flagged_reason}"
            )
            results.append({
                "period":        period,
                "actual_spend":  current_spend,
                "growth_pct":    None,
                "formula_shown": formula_str,
                "null_reason":   flagged_reason,
                "status":        "NULL_FLAGGED",
            })
            continue

        # Compute growth (enforcement rule 3 — show formula with substituted values)
        if prev_spend == 0:
            formula_str = f"({current_spend} - {prev_spend}) / {prev_spend} * 100 → division by zero"
            results.append({
                "period":        period,
                "actual_spend":  current_spend,
                "growth_pct":    None,
                "formula_shown": formula_str,
                "null_reason":   "",
                "status":        "DIV_BY_ZERO",
            })
            continue

        growth = (current_spend - prev_spend) / prev_spend * 100
        formula_str = f"({current_spend} - {prev_spend}) / {prev_spend} * 100"

        results.append({
            "period":        period,
            "actual_spend":  current_spend,
            "growth_pct":    round(growth, 1),
            "formula_shown": formula_str,
            "null_reason":   "",
            "status":        "OK",
        })

    return results


# ── Period helpers ────────────────────────────────────────────────────────────

def _previous_month(period: str) -> str:
    """Return YYYY-MM of the month before the given YYYY-MM."""
    year, month = int(period[:4]), int(period[5:7])
    if month == 1:
        return f"{year - 1:04d}-12"
    return f"{year:04d}-{month - 1:02d}"


def _previous_year(period: str) -> str:
    """Return YYYY-MM one year before the given YYYY-MM."""
    year, month = int(period[:4]), int(period[5:7])
    return f"{year - 1:04d}-{month:02d}"


# ── Output writers ────────────────────────────────────────────────────────────

def write_csv_output(
    output_path: str,
    ward: str,
    category: str,
    growth_type: str,
    results: List[Dict],
) -> None:
    """Write the per-period growth table to a CSV file."""
    fieldnames = [
        "period", "ward", "category", "growth_type",
        "actual_spend", "growth_pct", "formula_shown", "null_reason", "status",
    ]
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow({
                    "period":        row["period"],
                    "ward":          ward,
                    "category":      category,
                    "growth_type":   growth_type,
                    "actual_spend":  row["actual_spend"] if row["actual_spend"] is not None else "NULL",
                    "growth_pct":    row["growth_pct"]   if row["growth_pct"]   is not None else "NULL_FLAGGED",
                    "formula_shown": row["formula_shown"],
                    "null_reason":   row["null_reason"],
                    "status":        row["status"],
                })
    except (PermissionError, OSError) as exc:
        raise OSError(f"Cannot write output file '{output_path}': {exc}")


def print_summary(ward: str, category: str, growth_type: str, results: List[Dict]) -> None:
    """Print a human-readable summary table to stdout."""
    print(f"{'─' * 80}")
    print(f"Growth Report | Ward: {ward} | Category: {category} | Type: {growth_type}")
    print(f"{'─' * 80}")
    print(f"{'Period':<10} {'Actual Spend':>14} {'Growth %':>10}  {'Status':<14} Formula / Note")
    print(f"{'─' * 80}")
    for row in results:
        spend_str  = f"₹{row['actual_spend']:.1f}L" if row["actual_spend"] is not None else "NULL"
        growth_str = f"{row['growth_pct']:+.1f}%"    if row["growth_pct"]   is not None else "—"
        print(
            f"{row['period']:<10} {spend_str:>14} {growth_str:>10}  "
            f"{row['status']:<14} {row['formula_shown']}"
        )
        if row["null_reason"]:
            print(f"{'':>48} ↳ Null reason: {row['null_reason']}")
    print(f"{'─' * 80}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C — Budget Growth Calculator (per-ward, per-category, null-safe)"
    )
    parser.add_argument(
        "--input",       required=True,
        help="Path to ward_budget.csv"
    )
    parser.add_argument(
        "--ward",        required=True,
        help='Ward name exactly as in CSV, e.g. "Ward 1 – Kasba"'
    )
    parser.add_argument(
        "--category",    required=True,
        help='Category exactly as in CSV, e.g. "Roads & Pothole Repair"'
    )
    parser.add_argument(
        "--growth-type", required=False, default=None,
        dest="growth_type",
        help='Growth calculation type: MoM (month-on-month) or YoY (year-on-year). '
             'REQUIRED — system will refuse and exit if not supplied.'
    )
    parser.add_argument(
        "--output",      required=True,
        help="Path to write growth_output.csv"
    )
    args = parser.parse_args()

    # Enforcement rule 4: refuse if growth_type not provided
    if not args.growth_type:
        print(
            "[REFUSAL] --growth-type was not specified.\n"
            "You must explicitly provide one of: MoM, YoY.\n"
            "This system will never choose a growth type on your behalf.\n"
            "\nExample:\n"
            "  python app.py --input ... --ward ... --category ... "
            "--growth-type MoM --output ...",
            file=sys.stderr,
        )
        sys.exit(1)

    # ── Skill 1: load_dataset ─────────────────────────────────────────────────
    try:
        dataset = load_dataset(args.input)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Loaded {len(dataset['rows'])} rows total.")

    # ── Skill 2: compute_growth ───────────────────────────────────────────────
    try:
        results = compute_growth(
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type,
            dataset=dataset,
        )
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    # ── Print summary (enforcement rule 3 — formula visible) ──────────────────
    print_summary(args.ward, args.category, args.growth_type, results)

    # ── Write output CSV ──────────────────────────────────────────────────────
    try:
        write_csv_output(args.output, args.ward, args.category, args.growth_type, results)
    except OSError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"\n[INFO] Output written to: {args.output}")
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
