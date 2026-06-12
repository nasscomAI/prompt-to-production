"""
UC-0C — Budget Growth Analysis Agent
Built using the RICE → agents.md → skills.md → CRAFT workflow.

Failure modes guarded against:
  - Wrong aggregation level : output scoped to exactly one ward + category; cross-ward refused
  - Silent null handling    : nulls flagged before compute; never interpolated or skipped silently
  - Formula assumption      : --growth-type required; YoY refused on single-year data
  - Missing formula trail   : every computed row shows exact formula with values substituted
"""

import argparse
import csv
import sys
from typing import Optional

# ── Skill: load_dataset ────────────────────────────────────────────────────────

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(file_path: str, ward: str, category: str) -> dict:
    """
    Load ward_budget.csv, validate columns, filter by ward+category,
    report null rows before returning.

    Returns:
        {
            "rows": list[dict],       # filtered + sorted, all original columns
            "null_rows": list[dict],  # rows where actual_spend is null/blank
            "null_count": int,
            "total_count": int,
            "all_wards": list[str],
            "all_categories": list[str],
        }
    """
    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            all_rows = list(reader)
            fieldnames = set(reader.fieldnames or [])
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    # Validate required columns
    missing_cols = REQUIRED_COLUMNS - fieldnames
    if missing_cols:
        raise ValueError(f"Missing required columns: {sorted(missing_cols)}")

    all_wards      = sorted({r["ward"].strip() for r in all_rows if r["ward"].strip()})
    all_categories = sorted({r["category"].strip() for r in all_rows if r["category"].strip()})

    # Filter to requested ward + category
    filtered = [
        r for r in all_rows
        if r["ward"].strip() == ward and r["category"].strip() == category
    ]

    if not filtered:
        raise ValueError(
            f"No rows found for ward='{ward}', category='{category}'.\n"
            f"Available wards     : {all_wards}\n"
            f"Available categories: {all_categories}"
        )

    # Sort chronologically
    filtered.sort(key=lambda r: r["period"].strip())

    # Identify null rows
    null_rows = [r for r in filtered if not r["actual_spend"].strip()]

    # Print null report to stderr BEFORE returning
    if null_rows:
        print(f"\n[NULL REPORT] {len(null_rows)} null actual_spend row(s) in "
              f"ward='{ward}', category='{category}':", file=sys.stderr)
        for nr in null_rows:
            reason = nr.get("notes", "").strip() or "No reason in notes column"
            print(f"  • {nr['period'].strip()} — {reason}", file=sys.stderr)
        print("", file=sys.stderr)

    return {
        "rows":           filtered,
        "null_rows":      null_rows,
        "null_count":     len(null_rows),
        "total_count":    len(filtered),
        "all_wards":      all_wards,
        "all_categories": all_categories,
    }


# ── Skill: compute_growth ──────────────────────────────────────────────────────

def _parse_spend(raw: str) -> Optional[float]:
    """Return float or None if blank/invalid."""
    stripped = raw.strip()
    if not stripped:
        return None
    try:
        return float(stripped)
    except ValueError:
        return None


def _mom_prior_period(period: str) -> str:
    """Return the YYYY-MM of the month before `period`."""
    year, month = int(period[:4]), int(period[5:7])
    if month == 1:
        return f"{year - 1}-12"
    return f"{year}-{month - 1:02d}"


def compute_growth(data: dict, growth_type: str, ward: str, category: str) -> list[dict]:
    """
    Compute per-period growth for the loaded dataset slice.

    Returns list of dicts with full formula transparency and null flags.
    """
    # ── Enforcement: growth_type must be provided and valid ────────────────────
    if growth_type not in ("MoM", "YoY"):
        print(
            f"\n[REFUSED] --growth-type must be 'MoM' or 'YoY'. "
            f"Got: '{growth_type}'.\nThis agent will not choose a formula for you.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    rows     = data["rows"]
    periods  = {r["period"].strip(): r for r in rows}
    all_years = {r["period"].strip()[:4] for r in rows}

    # ── Enforcement: YoY on single-year dataset refused ────────────────────────
    if growth_type == "YoY":
        if len(all_years) < 2:
            print(
                f"\n[REFUSED] YoY growth requires at least 2 calendar years of data.\n"
                f"This dataset covers only: {sorted(all_years)}.\n"
                f"Use --growth-type MoM instead.",
                file=sys.stderr,
            )
            raise SystemExit(2)

    output_rows = []

    for row in rows:
        period  = row["period"].strip()
        current = _parse_spend(row["actual_spend"])
        notes   = row.get("notes", "").strip()
        is_null = current is None

        if growth_type == "MoM":
            prior_period_key = _mom_prior_period(period)
        else:
            # YoY: same month, prior year
            year, mo = int(period[:4]), int(period[5:7])
            prior_period_key = f"{year - 1}-{mo:02d}"

        prior_row   = periods.get(prior_period_key)
        prior_spend = _parse_spend(prior_row["actual_spend"]) if prior_row else None
        prior_null  = (prior_row is not None) and (prior_spend is None)

        # ── Determine growth_pct and formula_used ──────────────────────────────
        if prior_row is None and growth_type == "MoM":
            # First period — no prior
            growth_pct   = "N/A (first period)"
            formula_used = "N/A — first period, no prior month"
            prior_period_label = "N/A"
            prior_display      = "N/A"

        elif prior_row is None:
            growth_pct   = "N/A (prior period missing)"
            formula_used = "N/A — prior period missing from dataset"
            prior_period_label = prior_period_key
            prior_display      = "N/A"

        elif is_null:
            growth_pct   = "NULL — flagged"
            formula_used = "NULL — not computed (current period spend is null)"
            prior_period_label = prior_period_key
            prior_display      = f"{prior_spend:.1f}" if prior_spend is not None else "NULL"

        elif prior_null:
            growth_pct   = "NULL — flagged"
            formula_used = "NULL — not computed (prior period spend is null)"
            prior_period_label = prior_period_key
            prior_display      = "NULL"

        elif prior_spend == 0:
            growth_pct   = "N/A (prior spend = 0, division undefined)"
            formula_used = f"({current:.1f} − 0) / 0 × 100 — undefined"
            prior_period_label = prior_period_key
            prior_display      = "0.0"

        else:
            pct = (current - prior_spend) / prior_spend * 100
            sign = "+" if pct >= 0 else ""
            growth_pct   = f"{sign}{pct:.1f}%"
            formula_used = f"({current:.1f} − {prior_spend:.1f}) / {prior_spend:.1f} × 100"
            prior_period_label = prior_period_key
            prior_display      = f"{prior_spend:.1f}"

        output_rows.append({
            "period":        period,
            "ward":          ward,
            "category":      category,
            "actual_spend":  f"{current:.1f}" if current is not None else "NULL",
            "prior_period":  prior_period_label,
            "prior_spend":   prior_display,
            "growth_pct":    growth_pct,
            "formula_used":  formula_used,
            "null_flag":     "NULL" if is_null else "",
            "null_reason":   notes if is_null else "",
        })

    return output_rows


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C — Budget growth analytics agent (per-ward, per-category)"
    )
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help='Ward name, e.g. "Ward 1 – Kasba"')
    parser.add_argument("--category",    required=True,  help='Category, e.g. "Roads & Pothole Repair"')
    parser.add_argument("--growth-type", required=False, dest="growth_type",
                        help="Growth formula: MoM or YoY (REQUIRED — agent will refuse if absent)")
    parser.add_argument("--output",      required=True,  help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforcement: --growth-type is mandatory
    if not args.growth_type:
        print(
            "\n[REFUSED] --growth-type is required. This agent will not choose a formula.\n"
            "Specify --growth-type MoM  (Month-on-Month)\n"
            "      or --growth-type YoY  (Year-on-Year, requires 2+ years of data)\n",
            file=sys.stderr,
        )
        sys.exit(2)

    # Skill 1: load_dataset
    print(f"[INFO] Loading: {args.input}", file=sys.stderr)
    print(f"[INFO] Filter : ward='{args.ward}' | category='{args.category}'", file=sys.stderr)
    try:
        data = load_dataset(args.input, args.ward, args.category)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    print(
        f"[INFO] Loaded {data['total_count']} rows "
        f"({data['null_count']} null actual_spend).",
        file=sys.stderr,
    )

    # Skill 2: compute_growth
    print(f"[INFO] Computing {args.growth_type} growth...", file=sys.stderr)
    results = compute_growth(data, args.growth_type, args.ward, args.category)

    # Write CSV
    fieldnames = [
        "period", "ward", "category",
        "actual_spend", "prior_period", "prior_spend",
        "growth_pct", "formula_used",
        "null_flag", "null_reason",
    ]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # ── Console summary ────────────────────────────────────────────────────────
    null_rows    = [r for r in results if r["null_flag"] == "NULL"]
    computed     = [r for r in results if r["null_flag"] == "" and "%" in r["growth_pct"]]

    print(f"\n── Growth Report ───────────────────────────────────────")
    print(f"  Ward     : {args.ward}")
    print(f"  Category : {args.category}")
    print(f"  Type     : {args.growth_type}")
    print(f"  Periods  : {data['total_count']} | Computed: {len(computed)} | Nulls: {len(null_rows)}")
    print(f"  Output   : {args.output}")

    if null_rows:
        print(f"\n  ── NULL SUMMARY ({len(null_rows)} flagged rows) ──")
        for nr in null_rows:
            print(f"     • {nr['period']} | spend=NULL | reason: {nr['null_reason'] or 'none'}")

    print(f"\n  ── Computed Growth (spot-check) ──")
    for r in computed:
        print(f"     {r['period']}  {r['growth_pct']:>10}   {r['formula_used']}")

    print(f"────────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    main()
