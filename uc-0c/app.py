"""
UC-0C — Number That Looks Right
Implements load_dataset and compute_growth per agents.md (RICE) and skills.md.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


# ---------------------------------------------------------------------------
# Skill 1: load_dataset
# ---------------------------------------------------------------------------

def load_dataset(file_path: str, ward: str, category: str) -> dict:
    """
    Reads ward_budget.csv, validates columns, reports nulls, returns filtered rows.
    Refuses to proceed if ward or category is blank — no full-dataset aggregation.
    """
    if not ward or not ward.strip():
        print("ERROR: Ward must be specified — cannot operate on full dataset.", file=sys.stderr)
        sys.exit(1)
    if not category or not category.strip():
        print("ERROR: Category must be specified — cannot operate on full dataset.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            all_rows = list(reader)
            present = set(reader.fieldnames or [])
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    missing = REQUIRED_COLUMNS - present
    if missing:
        print(f"ERROR: Missing required column(s): {', '.join(sorted(missing))}", file=sys.stderr)
        sys.exit(1)

    # Filter to the requested ward + category
    filtered = [
        r for r in all_rows
        if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip()
    ]

    if not filtered:
        print(f"ERROR: No data found for '{ward}' / '{category}'. Check exact names.", file=sys.stderr)
        sys.exit(1)

    # Sort by period ascending
    filtered.sort(key=lambda r: r["period"])

    # Build null report — BEFORE any computation
    null_report = []
    for row in filtered:
        if not row["actual_spend"].strip():
            null_report.append({
                "period":   row["period"],
                "ward":     row["ward"],
                "category": row["category"],
                "notes":    row["notes"].strip() or "(no note provided)",
            })

    null_periods = [n["period"] for n in null_report]
    print(f"Loaded {len(filtered)} rows for '{ward}' / '{category}'. "
          f"Nulls found: {len(null_report)}"
          + (f" — {null_periods}" if null_report else "."))

    # Parse actual_spend to float where present
    rows_out = []
    for row in filtered:
        spend_raw = row["actual_spend"].strip()
        rows_out.append({
            "period":          row["period"],
            "ward":            row["ward"],
            "category":        row["category"],
            "budgeted_amount": float(row["budgeted_amount"]) if row["budgeted_amount"].strip() else None,
            "actual_spend":    float(spend_raw) if spend_raw else None,
            "notes":           row["notes"].strip(),
        })

    return {"rows": rows_out, "null_report": null_report}


# ---------------------------------------------------------------------------
# Skill 2: compute_growth
# ---------------------------------------------------------------------------

def compute_growth(rows: list, null_report: list, growth_type: str) -> list:
    """
    Computes per-period MoM or YoY growth with explicit formula per row.
    Null rows are flagged — never zero-filled, interpolated, or skipped silently.
    """
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            f"growth_type must be MoM or YoY — never inferred. "
            f"Got: '{growth_type}'. Please specify explicitly."
        )
    if not rows:
        raise ValueError("No rows to compute — check load_dataset output.")

    null_periods = {n["period"] for n in null_report}

    results = []
    for i, row in enumerate(rows):
        period = row["period"]
        spend  = row["actual_spend"]

        # Null row — flag and skip computation
        if spend is None:
            note = row["notes"] or "(no note)"
            results.append({
                "period":       period,
                "actual_spend": "NULL",
                "growth_value": "NULL — not computed",
                "formula":      "NULL — skipped",
                "flag":         f"NULL_SPEND — see notes: {note}",
            })
            continue

        # Find the reference period for growth calculation
        ref_row = None
        if growth_type == "MoM" and i > 0:
            ref_row = rows[i - 1]
        elif growth_type == "YoY":
            # Find row 12 periods earlier by period string (YYYY-MM)
            year  = int(period[:4])
            month = period[5:7]
            ref_period = f"{year - 1}-{month}"
            ref_matches = [r for r in rows if r["period"] == ref_period]
            ref_row = ref_matches[0] if ref_matches else None

        if ref_row is None:
            # First period or no prior year data — cannot compute
            results.append({
                "period":       period,
                "actual_spend": spend,
                "growth_value": "N/A — no prior period",
                "formula":      f"{growth_type}: no reference period available",
                "flag":         "",
            })
            continue

        ref_spend = ref_row["actual_spend"]

        if ref_spend is None:
            ref_note = ref_row["notes"] or "(no note)"
            results.append({
                "period":       period,
                "actual_spend": spend,
                "growth_value": "NULL — not computed",
                "formula":      f"{growth_type}: reference period {ref_row['period']} is NULL",
                "flag":         f"REF_NULL — reference period {ref_row['period']} has NULL_SPEND: {ref_note}",
            })
            continue

        if ref_spend == 0:
            results.append({
                "period":       period,
                "actual_spend": spend,
                "growth_value": "N/A — division by zero",
                "formula":      f"{growth_type}: ({spend} - {ref_spend}) / {ref_spend} × 100 — cannot divide by zero",
                "flag":         "DIV_ZERO",
            })
            continue

        growth = ((spend - ref_spend) / ref_spend) * 100
        sign   = "+" if growth >= 0 else ""
        formula = (
            f"{growth_type}: ({spend} - {ref_spend}) / {ref_spend} × 100 "
            f"= {sign}{growth:.1f}%"
        )

        results.append({
            "period":       period,
            "actual_spend": spend,
            "growth_value": f"{sign}{growth:.1f}%",
            "formula":      formula,
            "flag":         "",
        })

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Exact ward name")
    parser.add_argument("--category",    required=True,  help="Exact category name")
    parser.add_argument("--growth-type", required=True,  help="MoM or YoY")
    parser.add_argument("--output",      required=True,  help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforce: growth-type must be provided explicitly (never guessed)
    growth_type = args.growth_type.strip()
    if growth_type not in ("MoM", "YoY"):
        print(f"ERROR: --growth-type must be MoM or YoY. Got: '{growth_type}'", file=sys.stderr)
        sys.exit(1)

    # Skill 1: load and audit
    dataset = load_dataset(args.input, args.ward, args.category)

    # Print null report before computing
    if dataset["null_report"]:
        print("\nNULL ROWS (reported before computation):")
        for n in dataset["null_report"]:
            print(f"  {n['period']} — {n['ward']} / {n['category']} — Notes: {n['notes']}")
        print()

    # Skill 2: compute growth
    results = compute_growth(dataset["rows"], dataset["null_report"], growth_type)

    # Write output CSV
    fieldnames = ["period", "actual_spend", "growth_value", "formula", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Computed {len(results)} periods. Output written to {args.output}")


if __name__ == "__main__":
    main()
