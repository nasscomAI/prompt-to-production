"""
UC-0C app.py — Ward budget growth analyser.
Scoped to exactly one ward + one category per run; refuses rather than guesses
whenever an input is missing, ambiguous, or the data can't support the request.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
AGGREGATE_KEYWORDS = {"all", "*", "every", "total"}


def load_dataset(path: str):
    """Read ward_budget.csv, validate columns, and report null actual_spend rows up front."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"ward_budget.csv is missing required column(s): {sorted(missing)}")
        rows = list(reader)

    null_rows = [row for row in rows if not row["actual_spend"].strip()]
    return rows, null_rows


def _refuse(message: str):
    print(f"REFUSED: {message}", file=sys.stderr)
    sys.exit(1)


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """Per-period growth table for exactly one ward + one category. Refuses on ambiguity."""
    if ward.strip().lower() in AGGREGATE_KEYWORDS or category.strip().lower() in AGGREGATE_KEYWORDS:
        _refuse(
            "Aggregation across wards or categories is not supported - "
            "pass one specific --ward and one specific --category."
        )

    if growth_type not in ("MoM", "YoY"):
        _refuse("--growth-type must be exactly 'MoM' or 'YoY' — it was not specified or was invalid.")

    matched = sorted(
        (row for row in rows if row["ward"] == ward and row["category"] == category),
        key=lambda r: r["period"],
    )
    if not matched:
        available_wards = sorted({row["ward"] for row in rows})
        available_categories = sorted({row["category"] for row in rows})
        _refuse(
            f"No rows found for ward={ward!r} / category={category!r}. "
            f"Available wards: {available_wards}. Available categories: {available_categories}."
        )

    years = {row["period"][:4] for row in matched}
    if growth_type == "YoY" and len(years) < 2:
        _refuse(
            f"YoY growth requires more than one year of data; this dataset only covers {sorted(years)}."
        )

    step = 1 if growth_type == "MoM" else 12
    output = []
    for i, row in enumerate(matched):
        period = row["period"]
        current_raw = row["actual_spend"].strip()
        entry = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": current_raw or "",
            "growth_type": growth_type,
            "growth_pct": "",
            "formula": "",
            "flag": "",
            "reason": "",
        }

        if not current_raw:
            entry["flag"] = "NULL_ACTUAL_SPEND"
            entry["reason"] = row["notes"].strip() or "actual_spend is null; no reason given in notes."
            output.append(entry)
            continue

        prev_index = i - step
        if prev_index < 0:
            entry["flag"] = "NO_PRIOR_PERIOD"
            entry["reason"] = f"No period {step} step(s) before {period} in this ward/category's data."
            entry["formula"] = "(current - previous) / previous * 100"
            output.append(entry)
            continue

        prev_row = matched[prev_index]
        prev_raw = prev_row["actual_spend"].strip()
        if not prev_raw:
            entry["flag"] = "NULL_ACTUAL_SPEND"
            entry["reason"] = (
                f"Comparison period {prev_row['period']} has null actual_spend: "
                f"{prev_row['notes'].strip() or 'no reason given in notes.'}"
            )
            entry["formula"] = "(current - previous) / previous * 100"
            output.append(entry)
            continue

        current_val = float(current_raw)
        prev_val = float(prev_raw)
        growth_pct = (current_val - prev_val) / prev_val * 100
        entry["growth_pct"] = f"{growth_pct:.1f}"
        entry["formula"] = f"({current_val} - {prev_val}) / {prev_val} * 100"
        output.append(entry)

    return output


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Analyser")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name, e.g. 'Ward 1 – Kasba'")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                         help="MoM (month-over-month) or YoY (year-over-year)")
    parser.add_argument("--output", required=True, help="Path to write growth CSV")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    if null_rows:
        print(f"Note: {len(null_rows)} row(s) in the full dataset have null actual_spend.", file=sys.stderr)

    output_rows = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "actual_spend", "growth_type",
                  "growth_pct", "formula", "flag", "reason"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
