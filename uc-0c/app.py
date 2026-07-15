"""
UC-0C -- Number That Looks Right
Implements load_dataset and compute_growth using RICE enforcement rules
defined in agents.md and skills.md.

Core failure modes guarded against:
  - Wrong aggregation level  (scope enforced: single ward + single category only)
  - Silent null handling     (every null reported before computation)
  - Formula assumption       (growth_type required; formula shown in every row)
"""
import argparse
import csv
import sys
import os

# Reconfigure stdout to UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


# ──────────────────────────────────────────────────────────────────────────────
# SKILL: load_dataset
# ──────────────────────────────────────────────────────────────────────────────

def load_dataset(file_path: str) -> dict:
    """
    Read ward budget CSV, validate columns, report null actual_spend rows,
    return { "rows": [...], "null_report": [...] }.

    Enforcement:
    - Exit with code 1 if file or required columns missing.
    - Every null actual_spend row is reported to stdout.
    - Never silently skip a row.
    """
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    rows        = []
    null_report = []

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # ── Validate columns ───────────────────────────────────────────────
        if reader.fieldnames is None:
            print("ERROR: CSV has no header row.", file=sys.stderr)
            sys.exit(1)

        actual_cols = {c.strip() for c in reader.fieldnames}
        missing = REQUIRED_COLUMNS - actual_cols
        if missing:
            print(f"ERROR: Missing columns: {sorted(missing)}", file=sys.stderr)
            sys.exit(1)

        # ── Read rows ──────────────────────────────────────────────────────
        for idx, raw in enumerate(reader, start=2):
            row = {k.strip(): (v.strip() if v else "") for k, v in raw.items()}
            period   = row.get("period", "")
            ward     = row.get("ward", "")
            category = row.get("category", "")
            notes    = row.get("notes", "")

            # Parse budgeted_amount
            try:
                budgeted_amount = float(row.get("budgeted_amount", ""))
            except ValueError:
                budgeted_amount = None

            # Parse actual_spend (may be null)
            actual_spend_raw = row.get("actual_spend", "").strip()
            if actual_spend_raw == "":
                actual_spend = None
                null_report.append({
                    "period":      period,
                    "ward":        ward,
                    "category":    category,
                    "null_reason": notes if notes else "No reason in notes column",
                })
            else:
                try:
                    actual_spend = float(actual_spend_raw)
                except ValueError:
                    print(f"  WARNING row {idx}: actual_spend '{actual_spend_raw}' "
                          f"cannot be parsed as number -- treated as null "
                          f"(period={period}, ward={ward})")
                    actual_spend = None
                    null_report.append({
                        "period":      period,
                        "ward":        ward,
                        "category":    category,
                        "null_reason": f"Unparseable value: '{actual_spend_raw}'",
                    })

            rows.append({
                "period":           period,
                "ward":             ward,
                "category":         category,
                "budgeted_amount":  budgeted_amount,
                "actual_spend":     actual_spend,
                "notes":            notes,
            })

    # ── Print null report ──────────────────────────────────────────────────
    if null_report:
        print(f"\n  NULL ACTUAL_SPEND REPORT ({len(null_report)} rows):")
        print(f"  {'Period':<10} {'Ward':<30} {'Category':<30} Reason")
        print(f"  {'-'*10} {'-'*30} {'-'*30} {'-'*30}")
        for n in null_report:
            print(f"  {n['period']:<10} {n['ward']:<30} {n['category']:<30} {n['null_reason']}")
        print()
    else:
        print("  No null actual_spend values found.")

    return {"rows": rows, "null_report": null_report}


# ──────────────────────────────────────────────────────────────────────────────
# SKILL: compute_growth
# ──────────────────────────────────────────────────────────────────────────────

def compute_growth(rows: list, growth_type: str, ward: str, category: str) -> list:
    """
    Compute per-period growth for a single ward + category.

    Enforcement:
    - growth_type must be "MoM" or "YoY" — raise ValueError otherwise.
    - Null rows: growth_value = None, formula_used = None, null_flag set.
    - First row: growth_value = None, null_flag = "FIRST_PERIOD".
    - Formula shown in every non-null row.
    """
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            "Growth type not specified. "
            "Please provide growth_type='MoM' or 'YoY'. "
            "No computation performed."
        )

    if not rows:
        print(f"  WARNING: No rows found for ward='{ward}', category='{category}'.")
        return []

    # Sort by period ascending
    sorted_rows = sorted(rows, key=lambda r: r["period"])

    output = []
    prev_spend  = None
    prev_period = None

    for row in sorted_rows:
        period       = row["period"]
        actual_spend = row["actual_spend"]
        null_reason  = row.get("notes", "")

        # ── Null row ───────────────────────────────────────────────────────
        if actual_spend is None:
            output.append({
                "period":        period,
                "ward":          ward,
                "category":      category,
                "actual_spend":  None,
                "growth_value":  None,
                "formula_used":  None,
                "null_flag":     f"NULL -- {null_reason}" if null_reason else "NULL",
            })
            # Don't update prev_spend; can't compute growth from a null base
            continue

        # ── First non-null row ─────────────────────────────────────────────
        if prev_spend is None:
            output.append({
                "period":        period,
                "ward":          ward,
                "category":      category,
                "actual_spend":  actual_spend,
                "growth_value":  None,
                "formula_used":  None,
                "null_flag":     "FIRST_PERIOD",
            })
            prev_spend  = actual_spend
            prev_period = period
            continue

        # ── Division by zero guard ─────────────────────────────────────────
        if prev_spend == 0:
            output.append({
                "period":        period,
                "ward":          ward,
                "category":      category,
                "actual_spend":  actual_spend,
                "growth_value":  None,
                "formula_used":  f"({actual_spend} - {prev_spend}) / {prev_spend} x 100",
                "null_flag":     "COMPUTATION_ERROR -- prior period spend is 0",
            })
            prev_spend  = actual_spend
            prev_period = period
            continue

        # ── Compute growth ─────────────────────────────────────────────────
        growth_value = ((actual_spend - prev_spend) / prev_spend) * 100
        formula_used = (
            f"({actual_spend} - {prev_spend}) / {prev_spend} x 100"
            f" = {growth_value:+.1f}%"
        )

        output.append({
            "period":        period,
            "ward":          ward,
            "category":      category,
            "actual_spend":  actual_spend,
            "growth_value":  round(growth_value, 1),
            "formula_used":  formula_used,
            "null_flag":     "",
        })

        prev_spend  = actual_spend
        prev_period = period

    return output


# ──────────────────────────────────────────────────────────────────────────────
# CLI ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Analyser -- per-ward, per-category only"
    )
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Exact ward name string")
    parser.add_argument("--category",    required=True,  help="Exact category name string")
    parser.add_argument("--growth-type", required=False, dest="growth_type",
                        help="MoM or YoY (required for computation)")
    parser.add_argument("--output",      required=True,  help="Path to write growth_output.csv")
    args = parser.parse_args()

    print(f"\nUC-0C Budget Growth Analyser")
    print(f"  Input       : {args.input}")
    print(f"  Ward        : {args.ward}")
    print(f"  Category    : {args.category}")
    print(f"  Growth type : {args.growth_type}")
    print(f"  Output      : {args.output}")
    print(f"{'='*60}")

    # ── Enforcement: growth_type required ─────────────────────────────────
    if not args.growth_type:
        print(
            "\nERROR: Growth type not specified. "
            "Please provide --growth-type MoM or --growth-type YoY. "
            "No computation performed.",
            file=sys.stderr
        )
        sys.exit(1)

    growth_type = args.growth_type.strip().upper()
    if growth_type not in ("MOM", "YOY"):
        # normalise aliases
        if growth_type in ("MOM", "MONTH", "MONTH-ON-MONTH"):
            growth_type = "MoM"
        elif growth_type in ("YOY", "YEAR", "YEAR-ON-YEAR"):
            growth_type = "YoY"
        else:
            print(
                f"\nERROR: Invalid --growth-type '{args.growth_type}'. "
                "Must be 'MoM' or 'YoY'. No computation performed.",
                file=sys.stderr
            )
            sys.exit(1)
    else:
        growth_type = "MoM" if growth_type == "MOM" else "YoY"

    # ── Step 1: Load dataset ───────────────────────────────────────────────
    dataset = load_dataset(args.input)
    all_rows = dataset["rows"]

    # ── Enforcement: filter to single ward + single category ──────────────
    filtered = [
        r for r in all_rows
        if r["ward"] == args.ward and r["category"] == args.category
    ]

    if not filtered:
        print(
            f"\nERROR: No data found for ward='{args.ward}' and "
            f"category='{args.category}'. Check exact spelling.",
            file=sys.stderr
        )
        # List available wards and categories for guidance
        wards      = sorted({r["ward"] for r in all_rows})
        categories = sorted({r["category"] for r in all_rows})
        print(f"  Available wards      : {wards}")
        print(f"  Available categories : {categories}")
        sys.exit(1)

    print(f"  Rows matching filter : {len(filtered)}")

    # ── Step 2: Compute growth ─────────────────────────────────────────────
    try:
        results = compute_growth(filtered, growth_type, args.ward, args.category)
    except ValueError as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    # ── Step 3: Write output CSV ───────────────────────────────────────────
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_fields = ["period", "ward", "category", "actual_spend",
                     "growth_value", "formula_used", "null_flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n  Growth table written : {args.output}")

    # ── Step 4: Print table to console ────────────────────────────────────
    print(f"\n  {growth_type} GROWTH -- {args.ward} | {args.category}")
    print(f"  {'Period':<10} {'Spend':>10} {'Growth':>10}  Formula / Flag")
    print(f"  {'-'*10} {'-'*10} {'-'*10}  {'-'*40}")
    for r in results:
        spend   = f"{r['actual_spend']:.1f}" if r["actual_spend"] is not None else "NULL"
        growth  = f"{r['growth_value']:+.1f}%" if r["growth_value"] is not None else "  --  "
        detail  = r["formula_used"] or r["null_flag"]
        print(f"  {r['period']:<10} {spend:>10} {growth:>10}  {detail}")
    print()


if __name__ == "__main__":
    main()
