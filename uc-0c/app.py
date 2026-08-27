"""UC-0C Budget Growth Analysis Script.

Reads a ward-level budget CSV, filters by ward and category, and computes
growth metrics (MoM) for actual spend.

Usage:
  python app.py \
    --input ../data/budget/ward_budget.csv \
    --ward "Ward 1 – Kasba" \
    --category "Roads & Pothole Repair" \
    --growth-type MoM \
    --output growth_output.csv
"""

import argparse
import csv
import sys


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analysis")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to analyze")
    parser.add_argument("--category", required=True, help="Category to analyze")
    parser.add_argument(
        "--growth-type",
        required=True,
        choices=["MoM"],
        help="Growth type to compute (currently only MoM).",
    )
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    return parser.parse_args()


def _validate_input_columns(columns: list[str], required: list[str]):
    missing = [c for c in required if c not in columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")


def _normalize_key(value: str) -> str:
    return value.strip()


def _is_null(value: str) -> bool:
    return value is None or value.strip() == ""


def compute_growth(rows: list[dict], ward: str, category: str, output_path: str):
    # Sort by period (YYYY-MM sorts lexicographically)
    rows = sorted(rows, key=lambda r: r["period"])

    # Determine nulls and report
    null_rows = [r for r in rows if _is_null(r.get("actual_spend", ""))]
    if null_rows:
        print("Found rows with null actual_spend (will be flagged and not computed):")
        for r in null_rows:
            notes = r.get("notes", "").strip()
            reason = notes or "No notes provided"
            print(f"  {r.get('period')} — reason: {reason}")
        print()

    output_fields = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "growth_percent",
        "formula",
        "flag",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as out_f:
        writer = csv.DictWriter(out_f, fieldnames=output_fields)
        writer.writeheader()

        prev_spend = None
        for row in rows:
            period = row.get("period", "")
            spend_raw = row.get("actual_spend", "")
            flag = ""
            formula = ""
            growth_percent = ""

            if _is_null(spend_raw):
                flag = "MISSING"
                reason = row.get("notes", "").strip() or "No notes provided"
                formula = f"Missing actual_spend: {reason}"
            else:
                try:
                    spend = float(spend_raw)
                except ValueError:
                    flag = "INVALID"
                    formula = f"Invalid numeric actual_spend: {spend_raw}"
                    spend = None

                if spend is not None:
                    if prev_spend is None:
                        # Cannot compute without previous period
                        flag = "NO_BASE"
                        formula = "No previous period spend available"
                    else:
                        if prev_spend == 0:
                            flag = "DIV_ZERO"
                            formula = "Previous spend is 0, cannot compute growth"
                        else:
                            growth_percent = (spend - prev_spend) / prev_spend * 100
                            formula = "(current_month_spend - previous_month_spend) / previous_month_spend * 100"
            # Update prev_spend for next row only if current spend was valid
            if not _is_null(spend_raw):
                try:
                    prev_spend = float(spend_raw)
                except ValueError:
                    prev_spend = None

            writer.writerow({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": spend_raw,
                "growth_type": "MoM",
                "growth_percent": "" if growth_percent == "" else f"{growth_percent:.2f}",
                "formula": formula,
                "flag": flag,
            })


def main():
    args = _parse_args()

    if "," in args.ward or ";" in args.ward:
        raise SystemExit("Refuse: multiple wards provided; only a single ward is allowed.")
    if "," in args.category or ";" in args.category:
        raise SystemExit("Refuse: multiple categories provided; only a single category is allowed.")

    with open(args.input, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        _validate_input_columns(reader.fieldnames or [], [
            "period",
            "ward",
            "category",
            "actual_spend",
            "notes",
        ])
        filtered = [
            r for r in reader
            if _normalize_key(r.get("ward", "")) == args.ward
            and _normalize_key(r.get("category", "")) == args.category
        ]

    if not filtered:
        raise SystemExit(f"No rows found for ward '{args.ward}' and category '{args.category}'.")

    compute_growth(filtered, args.ward, args.category, args.output)
    print(f"Done. Output written to {args.output}")


if __name__ == "__main__":
    main()
