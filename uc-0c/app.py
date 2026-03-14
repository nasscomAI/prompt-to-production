"""
UC-0C app.py — Ward-Level Budget Growth Calculator.
Built following the RICE rules in agents.md and skills defined in skills.md.

Enforcement:
  - Never aggregate across wards or categories — only per-ward per-category output.
  - Flag every null actual_spend row before computing — report null reason from notes.
  - Show formula used in every output row alongside the result.
  - If --growth-type not specified — refuse and exit, never guess.
"""
import argparse
import csv
import sys


def load_dataset(filepath: str) -> tuple[list[dict], list[dict]]:
    """
    Load dataset from CSV file.
    Validates columns, reports null actual_spend rows and their reasons.
    Returns (valid_rows, null_rows).
    """
    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not required_cols.issubset(set(reader.fieldnames or [])):
            missing = required_cols - set(reader.fieldnames or [])
            print(f"[ERROR] CSV is missing required columns: {missing}", file=sys.stderr)
            sys.exit(1)

        valid_rows = []
        null_rows = []

        for rownum, row in enumerate(reader, start=2):  # row 1 = header
            spend = row.get("actual_spend", "").strip()
            if spend == "" or spend is None:
                null_rows.append({
                    "row": rownum,
                    "period": row.get("period", ""),
                    "ward": row.get("ward", ""),
                    "category": row.get("category", ""),
                    "reason": row.get("notes", "(no reason given)").strip() or "(no reason given)"
                })
            else:
                try:
                    row["actual_spend"] = float(spend)
                    row["budgeted_amount"] = float(row.get("budgeted_amount", 0) or 0)
                    valid_rows.append(row)
                except ValueError:
                    print(f"[WARN] Row {rownum}: non-numeric actual_spend '{spend}' — skipped", file=sys.stderr)

    return valid_rows, null_rows


def compute_growth(
    rows: list[dict],
    ward: str,
    category: str,
    growth_type: str,
) -> list[dict]:
    """
    Compute per-period growth for a specific ward + category.
    Returns a list of result dicts with formula shown.
    growth_type: 'MoM' (month-over-month) or 'YoY' (year-over-year).
    """
    # Filter to exactly ward + category — never aggregate across these dimensions
    filtered = [
        r for r in rows
        if r["ward"] == ward and r["category"] == category
    ]

    if not filtered:
        print(
            f"[ERROR] No data found for ward='{ward}', category='{category}'.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    results = []

    if growth_type == "MoM":
        # Month-over-month: compare period[i] to period[i-1]
        for i, row in enumerate(filtered):
            period = row["period"]
            spend = row["actual_spend"]
            if i == 0:
                results.append({
                    "ward": ward,
                    "category": category,
                    "period": period,
                    "actual_spend_lakh": round(spend, 2),
                    "growth_rate": "N/A (first period)",
                    "formula": "N/A (no prior month)",
                })
                continue

            prev = filtered[i - 1]
            prev_spend = prev["actual_spend"]
            prev_period = prev["period"]
            growth = ((spend - prev_spend) / prev_spend) * 100
            formula = f"({spend:.2f} - {prev_spend:.2f}) / {prev_spend:.2f} × 100"
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend_lakh": round(spend, 2),
                "growth_rate": f"{growth:+.1f}%",
                "formula": formula,
            })

    elif growth_type == "YoY":
        # Year-over-year: compare same month of previous year
        by_month = {r["period"][-2:]: r for r in filtered}  # keyed by MM
        for row in filtered:
            period = row["period"]
            spend = row["actual_spend"]
            month = period[-2:]
            year = period[:4]
            prev_period = f"{int(year) - 1}-{month}"
            if prev_period in {r["period"] for r in filtered}:
                prev_row = next(r for r in filtered if r["period"] == prev_period)
                prev_spend = prev_row["actual_spend"]
                growth = ((spend - prev_spend) / prev_spend) * 100
                formula = f"({spend:.2f} - {prev_spend:.2f}) / {prev_spend:.2f} × 100"
                results.append({
                    "ward": ward,
                    "category": category,
                    "period": period,
                    "actual_spend_lakh": round(spend, 2),
                    "growth_rate": f"{growth:+.1f}%",
                    "formula": formula,
                })
            else:
                results.append({
                    "ward": ward,
                    "category": category,
                    "period": period,
                    "actual_spend_lakh": round(spend, 2),
                    "growth_rate": "N/A (no prior year data)",
                    "formula": "N/A (no prior year)",
                })
    else:
        print(f"[ERROR] Unknown growth-type '{growth_type}'. Supported: MoM, YoY.", file=sys.stderr)
        sys.exit(1)

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Ward name (exact match)")
    parser.add_argument("--category",    required=True,  help="Category name (exact match)")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY")
    parser.add_argument("--output",      required=True,  help="Output CSV file path")
    args = parser.parse_args()

    # Enforcement: refuse if --growth-type not provided — never guess
    if not args.growth_type:
        print(
            "[REFUSED] --growth-type was not specified. Please provide 'MoM' or 'YoY'. "
            "This system never guesses the growth formula.",
            file=sys.stderr,
        )
        sys.exit(1)

    growth_type = args.growth_type.strip().upper()
    if growth_type not in ("MOM", "YOY"):
        print(
            f"[REFUSED] --growth-type '{args.growth_type}' is not recognised. "
            "Supported values: MoM, YoY.",
            file=sys.stderr,
        )
        sys.exit(1)
    growth_type = "MoM" if growth_type == "MOM" else "YoY"

    # Load and validate
    print(f"Loading dataset from {args.input} ...")
    valid_rows, null_rows = load_dataset(args.input)

    # Enforcement: flag every null row before computing
    if null_rows:
        print(f"\n[NULL REPORT] {len(null_rows)} row(s) with missing actual_spend — excluded from computation:")
        for n in null_rows:
            print(f"  Row {n['row']} | {n['period']} | {n['ward']} | {n['category']} | Reason: {n['reason']}")
        print()

    print(
        f"Computing {growth_type} growth for ward='{args.ward}', "
        f"category='{args.category}' ..."
    )
    results = compute_growth(valid_rows, args.ward, args.category, growth_type)

    # Write output CSV
    out_fields = ["ward", "category", "period", "actual_spend_lakh", "growth_rate", "formula"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. {len(results)} rows written to {args.output}")


if __name__ == "__main__":
    main()
