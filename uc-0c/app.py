"""
UC-0C — Budget Growth Analyser
Built using RICE → agents.md → skills.md → CRAFT workflow.

Rule-based implementation — no LLM, no API key, no external dependencies.
Uses only Python standard library.

Run:
    python app.py \
      --input ../data/budget/ward_budget.csv \
      --ward "Ward 1 – Kasba" \
      --category "Roads & Pothole Repair" \
      --growth-type MoM \
      --output growth_output.csv
"""
import argparse
import csv

EXPECTED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


# ---------------------------------------------------------------------------
# Skill: load_dataset
# ---------------------------------------------------------------------------

def load_dataset(file_path: str) -> list:
    """
    Read ward_budget.csv, validate columns, report all null actual_spend rows,
    then return the full dataset.

    Input:  file_path (str)
    Output: list of dicts, one per CSV row. Nulls are kept as None — never filled.
    """
    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not EXPECTED_COLUMNS.issubset(set(reader.fieldnames or [])):
                missing = EXPECTED_COLUMNS - set(reader.fieldnames or [])
                raise ValueError(f"load_dataset: missing columns: {missing}")
            rows = list(reader)
    except (FileNotFoundError, IOError) as e:
        raise RuntimeError(f"load_dataset: cannot read '{file_path}' — {e}") from e

    # Normalise actual_spend: blank → None, otherwise float
    for row in rows:
        val = row.get("actual_spend", "").strip()
        row["actual_spend"] = float(val) if val else None

    # --- Null report (agents.md enforcement rule 2) ---
    null_rows = [r for r in rows if r["actual_spend"] is None]
    if null_rows:
        print(f"\n[NULL REPORT] {len(null_rows)} null actual_spend row(s) found — these will NOT be computed:\n")
        for r in null_rows:
            reason = r.get("notes", "").strip() or "no reason given"
            print(f"  {r['period']}  |  {r['ward']}  |  {r['category']}  |  Reason: {reason}")
        print()

    return rows


# ---------------------------------------------------------------------------
# Skill: compute_growth
# ---------------------------------------------------------------------------

def compute_growth(rows: list, growth_type: str, ward: str, category: str) -> list:
    """
    Compute per-period growth for exactly one ward and one category.

    Input:  rows filtered to one ward + one category, growth_type ('MoM' or 'YoY'),
            ward (str), category (str)
    Output: list of dicts — period, actual_spend, growth_value, formula, flag
    """
    # --- Enforcement: refuse invalid growth_type (agents.md rule 4) ---
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            "Growth type not specified. Please provide --growth-type MoM or --growth-type YoY."
        )

    # --- Enforcement: refuse cross-ward/category data (agents.md rule 1) ---
    wards_in_data = {r["ward"] for r in rows}
    cats_in_data  = {r["category"] for r in rows}
    if len(wards_in_data) > 1 or len(cats_in_data) > 1:
        raise ValueError(
            "Cross-ward/category aggregation is not permitted. "
            "Please specify a single ward and a single category."
        )

    # Sort by period ascending
    sorted_rows = sorted(rows, key=lambda r: r["period"])

    results = []
    for i, row in enumerate(sorted_rows):
        period       = row["period"]
        actual_spend = row["actual_spend"]
        note         = row.get("notes", "").strip()

        # Null row — flag, do not compute (agents.md rule 2)
        if actual_spend is None:
            results.append({
                "period":       period,
                "actual_spend": "NULL",
                "growth_value": "",
                "formula":      "",
                "flag":         f"NULL — not computed | Reason: {note or 'no reason given'}",
            })
            continue

        # Find reference period value
        ref_value = None
        ref_label = ""

        if growth_type == "MoM":
            if i > 0:
                prev = sorted_rows[i - 1]
                ref_value = prev["actual_spend"]
                ref_label = prev["period"]
        else:  # YoY
            # Look for same month in prior year
            try:
                year, month = period.split("-")
                prior_period = f"{int(year) - 1}-{month}"
            except ValueError:
                prior_period = None
            if prior_period:
                match = next((r for r in sorted_rows if r["period"] == prior_period), None)
                if match:
                    ref_value = match["actual_spend"]
                    ref_label = prior_period

        if ref_value is None:
            # First period or no prior-year data — no basis for growth
            results.append({
                "period":       period,
                "actual_spend": f"{actual_spend:.1f}",
                "growth_value": "",
                "formula":      f"No prior {growth_type} period available",
                "flag":         "",
            })
        elif ref_value == 0:
            results.append({
                "period":       period,
                "actual_spend": f"{actual_spend:.1f}",
                "growth_value": "",
                "formula":      f"({actual_spend} − {ref_value}) / {ref_value} × 100 — division by zero",
                "flag":         "DIVISION_BY_ZERO",
            })
        else:
            growth = (actual_spend - ref_value) / ref_value * 100
            sign   = "+" if growth >= 0 else ""
            # agents.md enforcement rule 3 — show formula per row
            formula = (
                f"({actual_spend} − {ref_value}) / {ref_value} × 100 = {sign}{growth:.1f}%"
                f"  [ref: {ref_label}]"
            )
            results.append({
                "period":       period,
                "actual_spend": f"{actual_spend:.1f}",
                "growth_value": f"{sign}{growth:.1f}%",
                "formula":      formula,
                "flag":         "",
            })

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyser")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Exact ward name")
    parser.add_argument("--category",    required=True,  help="Exact category name")
    parser.add_argument("--growth-type", required=False, default=None,
                        dest="growth_type", help="MoM or YoY")
    parser.add_argument("--output",      required=True,  help="Path to write growth_output.csv")
    args = parser.parse_args()

    # --- Enforcement: refuse missing growth-type before doing any work ---
    if args.growth_type is None:
        print("ERROR: Growth type not specified. Please provide --growth-type MoM or --growth-type YoY.")
        raise SystemExit(1)

    # Skill 1: load
    all_rows = load_dataset(args.input)

    # Filter to requested ward + category
    filtered = [
        r for r in all_rows
        if r["ward"] == args.ward and r["category"] == args.category
    ]

    if not filtered:
        print(f"ERROR: No rows found for ward='{args.ward}' category='{args.category}'.")
        print("Available wards:     ", sorted({r['ward'] for r in all_rows}))
        print("Available categories:", sorted({r['category'] for r in all_rows}))
        raise SystemExit(1)

    # Skill 2: compute
    results = compute_growth(filtered, args.growth_type, args.ward, args.category)

    # Write output CSV
    output_fields = ["period", "actual_spend", "growth_value", "formula", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. {len(results)} rows written to {args.output}")
    print(f"Scope: {args.ward} | {args.category} | {args.growth_type}")


if __name__ == "__main__":
    main()
