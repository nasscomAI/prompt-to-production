"""
UC-0C — Number That Looks Right
Implemented according to agents.md (RICE) and skills.md.

Enforcement rules (from agents.md):
  1. Never aggregate across wards or categories — computation is per-ward per-category only.
     Refuse with exact message if all-ward aggregation is requested.
  2. Flag every null actual_spend row BEFORE computing — report period, ward, category,
     and null_reason from the notes column. Mark growth as NULL_FLAGGED, not computed.
  3. Show the formula used in every output row alongside the result.
     A result without a formula is a hard failure.
  4. If --growth-type is not specified: refuse with exact message, never default silently.

Context boundary (from agents.md):
  Only columns: period, ward, category, actual_spend, notes.
  budgeted_amount must NOT be used in growth calculations.
  No interpolation, no zero-fill for nulls.

Reference values (from agents.md / README):
  Ward 1 – Kasba · Roads & Pothole Repair · 2024-07 → +33.1% (MoM)
  Ward 1 – Kasba · Roads & Pothole Repair · 2024-10 → −34.8% (MoM)
"""

import argparse
import csv
import sys
from pathlib import Path

REQUIRED_COLUMNS = {"period", "ward", "category", "actual_spend", "notes"}

# Exact refuse messages from agents.md enforcement rules
MSG_NO_GROWTH_TYPE = (
    "Growth type not specified. "
    "Please provide --growth-type MoM or --growth-type YoY."
)
MSG_CROSS_WARD = (
    "Cross-ward aggregation is not supported. Please specify a single ward."
)

EXPECTED_NULL_COUNT = 5


# ─────────────────────────────────────────────────────────────────────────────
# Skill: load_dataset
# ─────────────────────────────────────────────────────────────────────────────

def load_dataset(file_path: str) -> dict:
    """
    Read ward_budget.csv, validate columns, surface all null actual_spend rows
    with their notes reasons BEFORE returning.

    Returns:
        {
          "data":       list of dicts (all rows),
          "null_rows":  list of dicts with period/ward/category/null_reason,
          "null_count": int,
          "summary":    str (printed to stdout before any computation),
        }

    Raises:
        FileNotFoundError  if file_path does not exist
        ValueError         if required columns are missing
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"Input file '{file_path}' appears to be empty.")
        fieldnames = set(reader.fieldnames)
        missing = REQUIRED_COLUMNS - fieldnames
        if missing:
            raise ValueError(
                f"Required column(s) missing from '{file_path}': {sorted(missing)}"
            )
        data = list(reader)

    # ── Identify null rows (enforcement rule 2) ───────────────────────────────
    null_rows = []
    for row in data:
        spend_raw = row.get("actual_spend", "").strip()
        if spend_raw == "":
            null_rows.append({
                "period":      row["period"],
                "ward":        row["ward"],
                "category":    row["category"],
                "null_reason": row.get("notes", "").strip() or "No reason given",
            })

    null_count = len(null_rows)
    if null_count != EXPECTED_NULL_COUNT:
        print(
            f"WARNING: Expected {EXPECTED_NULL_COUNT} null rows, found {null_count}.",
            file=sys.stderr,
        )

    # ── Build summary string (printed before any computation) ─────────────────
    lines = [
        "── UC-0C Null Row Report (surfaced before computation) ──────────────",
        f"  Total rows loaded : {len(data)}",
        f"  Null actual_spend : {null_count}",
    ]
    for nr in null_rows:
        lines.append(
            f"  NULL  {nr['period']}  |  {nr['ward']}  |  {nr['category']}"
            f"  →  \"{nr['null_reason']}\""
        )
    lines.append("─────────────────────────────────────────────────────────────────────")
    summary = "\n".join(lines)
    print(summary)
    print()

    return {
        "data":       data,
        "null_rows":  null_rows,
        "null_count": null_count,
        "summary":    summary,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Skill: compute_growth
# ─────────────────────────────────────────────────────────────────────────────

def _parse_spend(raw: str) -> float | None:
    """Return float or None if blank/invalid."""
    val = raw.strip()
    if not val:
        return None
    try:
        return float(val)
    except ValueError:
        return None


def _mom_growth(curr: float, prev: float) -> tuple[str, str]:
    """Return (growth_str, formula_str) for MoM."""
    pct = (curr - prev) / prev * 100
    sign = "+" if pct >= 0 else ""
    formula = f"({curr} − {prev}) / {prev} × 100 = {sign}{pct:.1f}%"
    return f"{sign}{pct:.1f}%", formula


def _yoy_growth(curr: float, prev: float) -> tuple[str, str]:
    """Return (growth_str, formula_str) for YoY."""
    pct = (curr - prev) / prev * 100
    sign = "+" if pct >= 0 else ""
    formula = f"({curr} − {prev}) / {prev} × 100 = {sign}{pct:.1f}%"
    return f"{sign}{pct:.1f}%", formula


def compute_growth(
    data: list[dict],
    ward: str,
    category: str,
    growth_type: str,
    null_rows: list[dict],
) -> list[dict]:
    """
    Calculate per-period growth for a single ward + category slice.

    Enforcement:
      - growth_type must be "MoM" or "YoY" (caller must validate before calling)
      - Null rows → growth = "NULL_FLAGGED", formula = "NULL — not computed: <reason>"
      - Formula shown in every row (enforcement rule 3)
      - budgeted_amount not used

    Raises:
        ValueError  if ward or category not found in dataset
    """
    # ── Filter to ward + category slice ──────────────────────────────────────
    slice_rows = [
        r for r in data
        if r["ward"] == ward and r["category"] == category
    ]
    if not slice_rows:
        all_wards = sorted({r["ward"] for r in data})
        all_cats  = sorted({r["category"] for r in data})
        raise ValueError(
            f"No data found for ward='{ward}', category='{category}'.\n"
            f"  Available wards     : {all_wards}\n"
            f"  Available categories: {all_cats}"
        )

    # Sort by period (YYYY-MM strings sort correctly lexicographically)
    slice_rows = sorted(slice_rows, key=lambda r: r["period"])

    # ── Build null lookup for quick access ────────────────────────────────────
    null_lookup = {
        (nr["period"], nr["ward"], nr["category"]): nr["null_reason"]
        for nr in null_rows
    }

    # ── Parse spend values ────────────────────────────────────────────────────
    periods = []
    for row in slice_rows:
        spend = _parse_spend(row["actual_spend"])
        null_reason = null_lookup.get((row["period"], row["ward"], row["category"]))
        periods.append({
            "period":      row["period"],
            "actual_spend": spend,
            "null_reason": null_reason,
        })

    # ── Compute growth per period ─────────────────────────────────────────────
    results = []

    for i, p in enumerate(periods):
        period      = p["period"]
        spend       = p["actual_spend"]
        null_reason = p["null_reason"]

        spend_display = f"{spend}" if spend is not None else "NULL"

        if spend is None:
            # Enforcement rule 2: flag, do not compute
            results.append({
                "period":       period,
                "ward":         ward,
                "category":     category,
                "actual_spend": "NULL",
                "null_reason":  null_reason,
                "growth":       "NULL_FLAGGED",
                "formula":      f"NULL — not computed: {null_reason}",
            })
            continue

        # First period: no prior value to compare against for MoM
        if growth_type == "MoM":
            if i == 0:
                results.append({
                    "period":       period,
                    "ward":         ward,
                    "category":     category,
                    "actual_spend": spend_display,
                    "null_reason":  "",
                    "growth":       "N/A",
                    "formula":      "N/A — no prior month",
                })
                continue

            prev = periods[i - 1]["actual_spend"]
            if prev is None:
                results.append({
                    "period":       period,
                    "ward":         ward,
                    "category":     category,
                    "actual_spend": spend_display,
                    "null_reason":  "",
                    "growth":       "NULL_FLAGGED",
                    "formula":      f"NULL — prior month ({periods[i-1]['period']}) is NULL_FLAGGED; cannot compute MoM",
                })
                continue

            growth, formula = _mom_growth(spend, prev)

        else:  # YoY
            # Find same month in previous year
            curr_year, curr_month = period.split("-")
            prev_period = f"{int(curr_year) - 1}-{curr_month}"
            prev_candidates = [p2 for p2 in periods if p2["period"] == prev_period]

            if not prev_candidates:
                results.append({
                    "period":       period,
                    "ward":         ward,
                    "category":     category,
                    "actual_spend": spend_display,
                    "null_reason":  "",
                    "growth":       "N/A",
                    "formula":      f"N/A — no data for prior year period {prev_period}",
                })
                continue

            prev = prev_candidates[0]["actual_spend"]
            if prev is None:
                results.append({
                    "period":       period,
                    "ward":         ward,
                    "category":     category,
                    "actual_spend": spend_display,
                    "null_reason":  "",
                    "growth":       "NULL_FLAGGED",
                    "formula":      f"NULL — prior year period {prev_period} is NULL_FLAGGED; cannot compute YoY",
                })
                continue

            growth, formula = _yoy_growth(spend, prev)

        results.append({
            "period":       period,
            "ward":         ward,
            "category":     category,
            "actual_spend": spend_display,
            "null_reason":  "",
            "growth":       growth,
            "formula":      formula,
        })

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Calculator — RICE-enforced, per-ward per-category"
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to ward_budget.csv",
    )
    parser.add_argument(
        "--ward", required=True,
        help='Exact ward name e.g. "Ward 1 – Kasba"',
    )
    parser.add_argument(
        "--category", required=True,
        help='Exact category name e.g. "Roads & Pothole Repair"',
    )
    parser.add_argument(
        "--growth-type", dest="growth_type", default=None,
        help="MoM or YoY",
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to write growth_output.csv",
    )
    args = parser.parse_args()

    # ── Enforcement rule 4: growth-type must be explicit ─────────────────────
    if args.growth_type is None:
        print(MSG_NO_GROWTH_TYPE)
        sys.exit(1)
    if args.growth_type not in ("MoM", "YoY"):
        print(MSG_NO_GROWTH_TYPE)
        sys.exit(1)

    # ── Enforcement rule 1: refuse cross-ward shortcut patterns ──────────────
    ward_lower = args.ward.strip().lower()
    if ward_lower in ("all", "all wards", "*", ""):
        print(MSG_CROSS_WARD)
        sys.exit(1)

    # ── Load ──────────────────────────────────────────────────────────────────
    dataset = load_dataset(args.input)

    # ── Compute ───────────────────────────────────────────────────────────────
    results = compute_growth(
        data        = dataset["data"],
        ward        = args.ward,
        category    = args.category,
        growth_type = args.growth_type,
        null_rows   = dataset["null_rows"],
    )

    # ── Write ─────────────────────────────────────────────────────────────────
    out_fields = ["period", "ward", "category", "actual_spend", "growth", "formula"]
    output_path = Path(args.output)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)

    # ── Summary ───────────────────────────────────────────────────────────────
    computed  = [r for r in results if r["growth"] not in ("NULL_FLAGGED", "N/A")]
    flagged   = [r for r in results if r["growth"] == "NULL_FLAGGED"]
    na_rows   = [r for r in results if r["growth"] == "N/A"]

    print("── UC-0C Growth Computation Summary ────────────────────────────────")
    print(f"  Ward             : {args.ward}")
    print(f"  Category         : {args.category}")
    print(f"  Growth type      : {args.growth_type}")
    print(f"  Total periods    : {len(results)}")
    print(f"  Computed         : {len(computed)}")
    print(f"  NULL_FLAGGED     : {len(flagged)}")
    print(f"  N/A (no prior)   : {len(na_rows)}")
    print(f"  Output written   : {output_path}")
    print("─────────────────────────────────────────────────────────────────────")
    print()

    # Print table to stdout for quick inspection
    print(f"{'Period':<10}  {'Spend':>8}  {'Growth':>10}  Formula")
    print("-" * 80)
    for r in results:
        print(
            f"{r['period']:<10}  {r['actual_spend']:>8}  {r['growth']:>10}  {r['formula']}"
        )
    print()
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
