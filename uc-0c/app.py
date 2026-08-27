"""UC-0C — Budget growth calculator."""
import argparse
import csv
from pathlib import Path


def compute_growth(input_path: str, ward: str, category: str, growth_type: str, output_path: str):
    """Compute month-over-month growth for one ward/category pair."""
    if not growth_type:
        raise ValueError("Please specify --growth-type (MoM or YoY).")

    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    selected = [row for row in rows if row.get("ward") == ward and row.get("category") == category]
    if not selected:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'.")

    selected.sort(key=lambda item: item["period"])

    output_rows = []
    for index, row in enumerate(selected):
        period = row["period"]
        actual = row.get("actual_spend", "")
        notes = row.get("notes", "")
        if actual in ("", None):
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "",
                "growth_pct": "",
                "status": "FLAGGED_NULL",
                "formula": "not computed because actual spend is missing",
                "notes": notes,
            })
            continue

        if index == 0:
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual,
                "growth_pct": "",
                "status": "baseline",
                "formula": "baseline month; no previous period",
                "notes": notes,
            })
            continue

        previous_row = selected[index - 1]
        previous_actual = previous_row.get("actual_spend", "")
        if previous_actual in ("", None):
            growth_pct = ""
            status = "FLAGGED_NULL"
            formula = "not computed because prior month actual spend is missing"
        else:
            prev_value = float(previous_actual)
            curr_value = float(actual)
            growth_pct = round(((curr_value - prev_value) / prev_value) * 100, 1) if prev_value else ""
            status = "ok"
            formula = f"(({curr_value} - {prev_value}) / {prev_value}) * 100"

        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual,
            "growth_pct": growth_pct,
            "status": status,
            "formula": formula,
            "notes": notes,
        })

    with output_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["period", "ward", "category", "actual_spend", "growth_pct", "status", "formula", "notes"])
        writer.writeheader()
        writer.writerows(output_rows)

    return output_path


def main():
    parser = argparse.ArgumentParser(description="UC-0C growth calculator")
    parser.add_argument("--input", required=True, help="Path to the budget CSV")
    parser.add_argument("--ward", required=True, help="Ward to evaluate")
    parser.add_argument("--category", required=True, help="Category to evaluate")
    parser.add_argument("--growth-type", required=True, help="Growth basis, e.g. MoM")
    parser.add_argument("--output", required=True, help="Path to write the growth CSV")
    args = parser.parse_args()
    output_path = compute_growth(args.input, args.ward, args.category, args.growth_type, args.output)
    print(f"Growth output written to {output_path}")


if __name__ == "__main__":
    main()
