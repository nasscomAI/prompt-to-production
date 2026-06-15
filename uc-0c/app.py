"""
UC-0C: Budget Growth Analysis Agent
Computes MoM or YoY actual_spend growth for a specific ward + category.
Flags null actual_spend rows before computation and shows the formula per row.

Usage:
    python app.py --ward "Ward 1 – Kasba" --category "Roads & Pothole Repair" --growth-type mom
    python app.py --ward "Ward 3 – Kothrud" --category "Parks & Greening" --growth-type yoy --output out.csv
"""
import argparse
import csv
import os
import sys
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "budget" / "ward_budget.csv"
DEFAULT_OUTPUT = Path(__file__).parent / "growth_output.csv"

OUTPUT_COLUMNS = [
    "period", "ward", "category", "budgeted_amount", "actual_spend",
    "growth_pct", "growth_type", "formula", "null_flag", "null_reason",
]


# ── Skill 1: load_ward_budget ────────────────────────────────────────────────

def load_ward_budget(ward: str, category: str, data_path: Path = DATA_PATH) -> list[dict]:
    """Load rows for exactly one ward and one category, sorted by period."""
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")

    rows = []
    with open(data_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["ward"].strip() == ward and row["category"].strip() == category:
                rows.append({
                    "period": row["period"].strip(),
                    "ward": row["ward"].strip(),
                    "category": row["category"].strip(),
                    "budgeted_amount": row["budgeted_amount"].strip(),
                    "actual_spend": row["actual_spend"].strip(),
                    "notes": row["notes"].strip(),
                })

    if not rows:
        raise ValueError(
            f"No data found for ward='{ward}' category='{category}'. "
            "Check exact spelling against ward_budget.csv."
        )

    rows.sort(key=lambda r: r["period"])
    return rows


# ── Skill 2: flag_null_spend ─────────────────────────────────────────────────

def flag_null_spend(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Separate rows with missing actual_spend; attach null_reason from notes."""
    computable, null_rows = [], []
    for row in rows:
        if row["actual_spend"] == "":
            null_rows.append({**row, "null_reason": row["notes"] or "No reason provided"})
        else:
            computable.append(row)
    return computable, null_rows


# ── Skill 3: compute_mom_growth ──────────────────────────────────────────────

def compute_mom_growth(rows: list[dict]) -> list[dict]:
    """Add MoM growth_pct and formula to each row; None for the first period."""
    enriched = []
    for i, row in enumerate(rows):
        current = float(row["actual_spend"])
        if i == 0:
            enriched.append({**row, "growth_pct": None, "growth_type": "MoM",
                              "formula": "N/A — no prior period"})
        else:
            prev = float(rows[i - 1]["actual_spend"])
            pct = round((current - prev) / prev * 100, 4)
            formula = (
                f"({current} - {prev}) / {prev} x 100 = {pct}%  "
                f"[period {rows[i-1]['period']} -> {row['period']}]"
            )
            enriched.append({**row, "growth_pct": pct, "growth_type": "MoM", "formula": formula})
    return enriched


# ── Skill 4: compute_yoy_growth ──────────────────────────────────────────────

def compute_yoy_growth(rows: list[dict]) -> list[dict]:
    """Add YoY growth_pct and formula; None when the prior-year period is absent."""
    by_period = {r["period"]: float(r["actual_spend"]) for r in rows}
    enriched = []
    for row in rows:
        current = float(row["actual_spend"])
        year, month = row["period"].split("-")
        prior_period = f"{int(year) - 1:04d}-{month}"
        if prior_period in by_period:
            prior = by_period[prior_period]
            pct = round((current - prior) / prior * 100, 4)
            formula = (
                f"({current} - {prior}) / {prior} x 100 = {pct}%  "
                f"[{prior_period} -> {row['period']}]"
            )
            enriched.append({**row, "growth_pct": pct, "growth_type": "YoY", "formula": formula})
        else:
            enriched.append({**row, "growth_pct": None, "growth_type": "YoY",
                              "formula": f"N/A — no prior year period ({prior_period} missing)"})
    return enriched


# ── Skill 5: generate_growth_output ─────────────────────────────────────────

def generate_growth_output(
    growth_rows: list[dict],
    null_rows: list[dict],
    output_path: Path = DEFAULT_OUTPUT,
) -> None:
    """Write growth_output.csv combining computed and null rows, sorted by period."""
    if not growth_rows and not null_rows:
        raise ValueError("No rows to write — both growth_rows and null_rows are empty.")

    all_rows = []
    for r in growth_rows:
        all_rows.append({
            "period": r["period"], "ward": r["ward"], "category": r["category"],
            "budgeted_amount": r["budgeted_amount"], "actual_spend": r["actual_spend"],
            "growth_pct": r.get("growth_pct", ""), "growth_type": r.get("growth_type", ""),
            "formula": r.get("formula", ""), "null_flag": False, "null_reason": "",
        })
    for r in null_rows:
        all_rows.append({
            "period": r["period"], "ward": r["ward"], "category": r["category"],
            "budgeted_amount": r["budgeted_amount"], "actual_spend": "",
            "growth_pct": "", "growth_type": "", "formula": "",
            "null_flag": True, "null_reason": r.get("null_reason", ""),
        })

    all_rows.sort(key=lambda r: r["period"])

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
            writer.writeheader()
            writer.writerows(all_rows)
    except OSError as e:
        raise IOError(f"Cannot write to {output_path}: {e}") from e

    print(f"[OK] Written {len(all_rows)} rows to {output_path}")


# ── CLI entry-point ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Budget growth analysis agent — UC-0C",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  python app.py --ward "Ward 1 – Kasba" '
            '--category "Roads & Pothole Repair" --growth-type mom\n'
            '  python app.py --ward "Ward 3 – Kothrud" '
            '--category "Parks & Greening" --growth-type yoy --output out.csv'
        ),
    )
    parser.add_argument("--ward", required=True,
                        help="Exact ward name as it appears in ward_budget.csv")
    parser.add_argument("--category", required=True,
                        help="Exact category name as it appears in ward_budget.csv")
    parser.add_argument(
        "--growth-type", required=True, choices=["mom", "yoy"],
        help="Growth calculation type: 'mom' (month-over-month) or 'yoy' (year-over-year). "
             "This argument is mandatory — the agent never assumes a default.",
    )
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT),
                        help=f"Output CSV path (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--data", default=str(DATA_PATH),
                        help=f"Source CSV path (default: {DATA_PATH})")

    args = parser.parse_args()

    data_path = Path(args.data)
    output_path = Path(args.output)

    # ── Step 1: load ────────────────────────────────────────────────────────
    try:
        rows = load_ward_budget(args.ward, args.category, data_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(rows)} rows for ward='{args.ward}' category='{args.category}'")

    # ── Step 2: flag nulls ──────────────────────────────────────────────────
    computable, null_rows = flag_null_spend(rows)

    if null_rows:
        print(f"\n[WARN] {len(null_rows)} row(s) with missing actual_spend (excluded from growth):")
        for r in null_rows:
            print(f"   period={r['period']}  null_reason='{r['null_reason']}'")
    else:
        print("  No null actual_spend rows found.")

    # ── Step 3: compute growth ──────────────────────────────────────────────
    if not computable:
        print("\nERROR: All rows have null actual_spend — cannot compute growth.", file=sys.stderr)
        sys.exit(1)

    if args.growth_type == "mom":
        growth_rows = compute_mom_growth(computable)
    else:
        growth_rows = compute_yoy_growth(computable)

    print(f"\nGrowth computed ({args.growth_type.upper()}) for {len(growth_rows)} row(s):")
    for r in growth_rows:
        pct = f"{r['growth_pct']}%" if r["growth_pct"] is not None else "N/A"
        print(f"  {r['period']}  growth_pct={pct:>10}  formula: {r['formula']}")

    # ── Step 4: write output ────────────────────────────────────────────────
    try:
        generate_growth_output(growth_rows, null_rows, output_path)
    except (IOError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

