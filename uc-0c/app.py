"""
UC-0C — Number That Looks Right
Municipal budget growth analyst agent.

Enforcement rules (from agents.md):
  1. Never aggregate across wards or categories — refuse if ward/category not specified.
  2. Flag every null actual_spend row (with notes reason) before computing.
  3. Every output row includes the explicit formula used.
  4. If --growth-type not provided — refuse; never guess.
  5. Null rows appear in output with growth_value=NULL, null_flag=TRUE.
  6. Never interpolate or impute null actual_spend values.
"""

import argparse
import csv
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Skill: load_dataset
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
PERIOD_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def load_dataset(file_path: str) -> dict:
    """
    Reads the ward_budget CSV, validates columns, reports null count and
    which rows contain null actual_spend before returning the dataset.

    Returns:
        {
            "data": list[dict],
            "null_report": list[dict],
            "null_count": int,
            "malformed_report": list[dict]   # rows where actual_spend is neither float nor blank
        }

    Raises:
        SystemExit on any fatal validation error (FileNotFoundError,
        missing columns, bad period format, empty dataset).
    """
    path = Path(file_path)

    # --- existence check ---
    if not path.exists():
        sys.exit(
            f"[load_dataset] ERROR — FileNotFoundError: '{file_path}' does not exist or cannot be read."
        )

    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)

        # --- column validation ---
        if reader.fieldnames is None:
            sys.exit("[load_dataset] ERROR — EmptyDatasetError: CSV has no header row.")

        present = {c.strip().lower() for c in reader.fieldnames}
        missing = REQUIRED_COLUMNS - present
        if missing:
            sys.exit(
                f"[load_dataset] ERROR — Missing required columns: {sorted(missing)}.\n"
                f"  Found columns: {sorted(present)}"
            )

        rows = list(reader)

    # --- empty dataset check ---
    if not rows:
        sys.exit("[load_dataset] ERROR — EmptyDatasetError: CSV contains no data rows.")

    # --- period format + actual_spend type validation ---
    bad_periods = []
    malformed_spend = []
    data = []
    null_report = []

    for i, raw in enumerate(rows, start=2):  # row 2 = first data row
        row = {k.strip().lower(): v.strip() for k, v in raw.items()}

        # period format
        if not PERIOD_RE.match(row.get("period", "")):
            bad_periods.append({"row_number": i, "period_value": row.get("period", "")})

        # actual_spend: blank → null, valid float → keep, else → malformed
        spend_raw = row.get("actual_spend", "")
        if spend_raw == "":
            row["actual_spend"] = None
            null_report.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "notes": row.get("notes", ""),
                }
            )
        else:
            try:
                row["actual_spend"] = float(spend_raw)
            except ValueError:
                malformed_spend.append(
                    {"row_number": i, "actual_spend_value": spend_raw, "period": row.get("period")}
                )
                row["actual_spend"] = None  # treat as null for safety but flag it

        # budgeted_amount — coerce quietly (not an enforcement concern)
        try:
            row["budgeted_amount"] = float(row.get("budgeted_amount", ""))
        except ValueError:
            row["budgeted_amount"] = None

        data.append(row)

    if bad_periods:
        lines = "\n".join(
            f"  row {r['row_number']}: '{r['period_value']}'" for r in bad_periods
        )
        sys.exit(
            f"[load_dataset] ERROR — {len(bad_periods)} period value(s) do not conform to YYYY-MM:\n{lines}"
        )

    return {
        "data": data,
        "null_report": null_report,
        "null_count": len(null_report),
        "malformed_report": malformed_spend,
    }


# ---------------------------------------------------------------------------
# Skill: compute_growth
# ---------------------------------------------------------------------------

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filters to a single ward + category, then computes MoM or YoY growth
    per period. Returns a per-period list with formula_used and null_flag.

    Enforcement:
      - growth_type must be exactly "MoM" or "YoY" — never guessed.
      - ward and category must be single exact strings — never lists.
      - Null actual_spend rows → growth_value=None, formula_used=None, null_flag=True.
      - Previous-period null → current growth_value=None (no stale denominator).
      - Multi-ward / multi-category lists → refused.

    Raises:
        SystemExit on enforcement violations or no matching rows.
    """

    # --- guard: no aggregation ---
    if isinstance(ward, list) or isinstance(category, list):
        sys.exit(
            "[compute_growth] REFUSED — aggregation across multiple wards or categories "
            "is not permitted. Supply exactly one ward and one category."
        )

    # --- guard: growth_type must be explicit ---
    if growth_type is None or growth_type not in ("MoM", "YoY"):
        sys.exit(
            "[compute_growth] REFUSED — --growth-type must be explicitly set to 'MoM' or 'YoY'.\n"
            "  Never assumed or defaulted. Please re-run with --growth-type MoM or --growth-type YoY."
        )

    # --- guard: ward and category must be provided ---
    if not ward or not category:
        sys.exit(
            "[compute_growth] REFUSED — both --ward and --category must be supplied. "
            "Single ward + category queries only."
        )

    # --- filter ---
    valid_wards = sorted({r["ward"] for r in data})
    valid_cats = sorted({r["category"] for r in data})

    if ward not in valid_wards:
        sys.exit(
            f"[compute_growth] ERROR — ward '{ward}' not found in dataset.\n"
            f"  Valid wards: {valid_wards}"
        )
    if category not in valid_cats:
        sys.exit(
            f"[compute_growth] ERROR — category '{category}' not found in dataset.\n"
            f"  Valid categories: {valid_cats}"
        )

    subset = [r for r in data if r["ward"] == ward and r["category"] == category]

    if not subset:
        sys.exit(
            f"[compute_growth] ERROR — EmptyFilterError: no rows found for "
            f"ward='{ward}', category='{category}'."
        )

    # sort by period (YYYY-MM sorts correctly as strings)
    subset.sort(key=lambda r: r["period"])

    # --- build a period→spend lookup for YoY back-reference ---
    spend_by_period = {r["period"]: r["actual_spend"] for r in subset}

    results = []
    for row in subset:
        period = row["period"]
        actual_spend = row["actual_spend"]
        notes = row.get("notes", "")

        # --- null row: flag, never compute ---
        if actual_spend is None:
            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": None,
                    "growth_value": None,
                    "formula_used": None,
                    "null_flag": True,
                    "null_reason": notes,
                }
            )
            continue

        # --- find previous period value ---
        if growth_type == "MoM":
            prev_period = _previous_month(period)
        else:  # YoY
            prev_period = _previous_year(period)

        prev_spend = spend_by_period.get(prev_period)  # None if not in subset or null

        # previous is null or missing → cannot compute; flag this row too
        if prev_spend is None:
            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": actual_spend,
                    "growth_value": None,
                    "formula_used": None,
                    "null_flag": True,
                    "null_reason": (
                        f"Previous period ({prev_period}) is null or absent — growth not computed"
                    ),
                }
            )
            continue

        # previous is zero → division undefined
        if prev_spend == 0.0:
            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": actual_spend,
                    "growth_value": None,
                    "formula_used": None,
                    "null_flag": True,
                    "null_reason": f"Previous period ({prev_period}) actual_spend is 0 — division undefined",
                }
            )
            continue

        # --- compute ---
        raw_growth = (actual_spend - prev_spend) / prev_spend
        sign = "+" if raw_growth >= 0 else ""
        growth_pct = f"{sign}{raw_growth * 100:.1f}%"
        formula = (
            f"({actual_spend} - {prev_spend}) / {prev_spend} = {growth_pct}"
        )

        results.append(
            {
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual_spend,
                "growth_value": growth_pct,
                "formula_used": formula,
                "null_flag": False,
                "null_reason": None,
            }
        )

    return results


# ---------------------------------------------------------------------------
# Period helpers
# ---------------------------------------------------------------------------

def _previous_month(period: str) -> str:
    year, month = int(period[:4]), int(period[5:])
    if month == 1:
        return f"{year - 1}-12"
    return f"{year}-{month - 1:02d}"


def _previous_year(period: str) -> str:
    year, month = int(period[:4]), int(period[5:])
    return f"{year - 1}-{month:02d}"


# ---------------------------------------------------------------------------
# Output writer
# ---------------------------------------------------------------------------

OUTPUT_FIELDS = [
    "period", "ward", "category", "actual_spend",
    "growth_value", "formula_used", "null_flag", "null_reason",
]


def write_output(results: list, output_path: str) -> None:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for row in results:
            writer.writerow(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "actual_spend": "" if row["actual_spend"] is None else row["actual_spend"],
                    "growth_value": "" if row["growth_value"] is None else row["growth_value"],
                    "formula_used": "" if row["formula_used"] is None else row["formula_used"],
                    "null_flag": "TRUE" if row["null_flag"] else "FALSE",
                    "null_reason": "" if row["null_reason"] is None else row["null_reason"],
                }
            )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="UC-0C — Municipal budget growth analyst (MoM / YoY)."
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help='Exact ward name e.g. "Ward 1 – Kasba"')
    parser.add_argument("--category", required=True, help='Exact category e.g. "Roads & Pothole Repair"')
    parser.add_argument(
        "--growth-type",
        dest="growth_type",
        default=None,
        choices=["MoM", "YoY"],
        help="Growth type: MoM (month-over-month) or YoY (year-over-year). Required.",
    )
    parser.add_argument("--output", required=True, help="Path for output CSV")
    return parser.parse_args()


def main():
    args = parse_args()

    # Enforcement: growth-type must be explicit
    if args.growth_type is None:
        sys.exit(
            "[REFUSED] --growth-type was not supplied.\n"
            "  Please re-run with --growth-type MoM or --growth-type YoY.\n"
            "  This agent never guesses or defaults the growth type."
        )

    # ── SKILL 1: load_dataset ──────────────────────────────────────────────
    print(f"\n[load_dataset] Reading: {args.input}")
    dataset = load_dataset(args.input)

    # Report malformed rows if any
    if dataset["malformed_report"]:
        print(
            f"\n[load_dataset] WARNING — {len(dataset['malformed_report'])} malformed actual_spend value(s) "
            f"(neither float nor blank):"
        )
        for m in dataset["malformed_report"]:
            print(f"  row {m['row_number']} | period={m['period']} | value='{m['actual_spend_value']}'")

    # Enforcement: report every null row BEFORE computing
    print(f"\n[load_dataset] Null actual_spend count: {dataset['null_count']}")
    if dataset["null_report"]:
        print("[load_dataset] Null rows (growth will NOT be computed for these):")
        for n in dataset["null_report"]:
            print(
                f"  period={n['period']} | ward={n['ward']} | "
                f"category={n['category']} | reason='{n['notes']}'"
            )
    else:
        print("[load_dataset] No null actual_spend rows found.")

    print(f"\n[load_dataset] Dataset loaded: {len(dataset['data'])} rows total.")

    # ── SKILL 2: compute_growth ────────────────────────────────────────────
    print(
        f"\n[compute_growth] Computing {args.growth_type} growth for:\n"
        f"  ward     = {args.ward}\n"
        f"  category = {args.category}\n"
    )

    results = compute_growth(
        data=dataset["data"],
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type,
    )

    # ── Write output ───────────────────────────────────────────────────────
    write_output(results, args.output)
    print(f"[output] Written {len(results)} rows → {args.output}")

    # ── Console summary ────────────────────────────────────────────────────
    print("\n── Output summary ──────────────────────────────────────────────")
    header = f"{'Period':<10}  {'Actual Spend':>14}  {'Growth':>10}  {'Null?':>6}  Formula"
    print(header)
    print("─" * 90)
    for r in results:
        spend_str = f"₹{r['actual_spend']:.1f}L" if r["actual_spend"] is not None else "NULL"
        growth_str = r["growth_value"] if r["growth_value"] else "NULL"
        null_str = "TRUE" if r["null_flag"] else "FALSE"
        formula_str = r["formula_used"] if r["formula_used"] else f"— {r['null_reason']}"
        print(f"{r['period']:<10}  {spend_str:>14}  {growth_str:>10}  {null_str:>6}  {formula_str}")


if __name__ == "__main__":
    main()