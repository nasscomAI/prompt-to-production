"""
UC-0C app.py — Strict ward/category growth calculator.
"""
import argparse
import csv


REQUIRED_FIELDS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(input_path: str) -> list[dict]:
    """Load the budget dataset and validate the expected schema."""
    with open(input_path, "r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        if reader.fieldnames is None:
            raise ValueError("The input CSV is missing a header row.")

        missing_fields = sorted(REQUIRED_FIELDS.difference(reader.fieldnames))
        if missing_fields:
            raise ValueError(f"Missing required columns: {', '.join(missing_fields)}")

        rows = []
        for row in reader:
            cleaned = {key: (value.strip() if isinstance(value, str) else value) for key, value in row.items()}
            rows.append(cleaned)

        return rows


def compute_growth(rows: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    """Compute growth for one ward and category using the requested formula."""
    if growth_type not in {"MoM", "YoY"}:
        raise ValueError("Growth type must be exactly 'MoM' or 'YoY'.")

    filtered_rows = [row for row in rows if row.get("ward") == ward and row.get("category") == category]
    if not filtered_rows:
        raise ValueError(f"No rows found for ward '{ward}' and category '{category}'.")

    filtered_rows.sort(key=lambda row: row["period"])

    results = []
    previous_actual = None

    for row in filtered_rows:
        period = row["period"]
        ward_name = row["ward"]
        category_name = row["category"]
        actual_raw = row.get("actual_spend", "")
        notes = row.get("notes", "")

        if not actual_raw:
            results.append(
                {
                    "period": period,
                    "ward": ward_name,
                    "category": category_name,
                    "actual_spend": "",
                    "growth_percent": "",
                    "formula": "Not computed: actual_spend is null",
                    "status": "FLAGGED",
                    "null_reason": notes or "No reason provided",
                }
            )
            previous_actual = None
            continue

        actual = float(actual_raw)
        formula = ""
        growth = ""
        status = "computed"

        if growth_type == "MoM":
            if previous_actual is None or previous_actual == 0:
                growth = ""
                formula = "MoM: baseline (no previous period in the selected scope)"
                status = "baseline"
            else:
                growth_value = (actual - previous_actual) / previous_actual if previous_actual else 0.0
                growth = f"{growth_value:.1%}"
                formula = f"MoM: ({actual:.1f} - {previous_actual:.1f}) / {previous_actual:.1f}"
        else:
            month_key = period[5:]
            previous_year_period = f"{int(period[:4]) - 1}-{month_key}"
            previous_rows = {r["period"]: float(r["actual_spend"]) for r in filtered_rows if r.get("actual_spend")}
            previous_actual = previous_rows.get(previous_year_period)

            if previous_actual is None or previous_actual == 0:
                growth = ""
                formula = "YoY: not computed (no prior-year data for the same month)"
                status = "insufficient_history"
            else:
                growth_value = (actual - previous_actual) / previous_actual if previous_actual else 0.0
                growth = f"{growth_value:.1%}"
                formula = f"YoY: ({actual:.1f} - {previous_actual:.1f}) / {previous_actual:.1f}"

        results.append(
            {
                "period": period,
                "ward": ward_name,
                "category": category_name,
                "actual_spend": f"{actual:.1f}",
                "growth_percent": growth,
                "formula": formula,
                "status": status,
                "null_reason": "",
            }
        )

        previous_actual = actual

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C growth calculator")
    parser.add_argument("--input", required=True, help="Path to input budget CSV")
    parser.add_argument("--ward", required=True, help="Single ward to analyze")
    parser.add_argument("--category", required=True, help="Single category to analyze")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth formula to use")
    parser.add_argument("--output", required=True, help="Path to write the output CSV")
    args = parser.parse_args()

    try:
        rows = load_dataset(args.input)
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
    except Exception as exc:
        raise SystemExit(f"Refusing to proceed: {exc}") from exc

    with open(args.output, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=["period", "ward", "category", "actual_spend", "growth_percent", "formula", "status", "null_reason"],
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Wrote {args.output}")


if __name__ == "__main__":
    main()
