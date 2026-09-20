import argparse
import csv
from typing import Dict, List, Optional, Tuple


REQUIRED_FIELDS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(input_path: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """Load and validate the budget dataset, returning rows and null rows."""
    with open(input_path, "r", newline="", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        missing = REQUIRED_FIELDS - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"Dataset is missing required field(s): {', '.join(sorted(missing))}")
        rows = list(reader)

    if not rows:
        raise ValueError("Dataset is empty")
    for row in rows:
        try:
            float(row["budgeted_amount"])
            if row["actual_spend"].strip():
                float(row["actual_spend"])
        except ValueError as error:
            raise ValueError(f"Invalid numeric value in period {row['period']}: {error}") from error
    null_rows = [row for row in rows if not row["actual_spend"].strip()]
    return rows, null_rows


def compute_growth(
    rows: List[Dict[str, str]], ward: str, category: str, growth_type: str
) -> List[Dict[str, str]]:
    """Compute growth for one ward/category without aggregating other rows."""
    growth_type = growth_type.upper()
    if growth_type not in {"MOM", "YOY"}:
        raise ValueError("Unsupported growth type; choose MoM or YoY")
    if ward.strip().casefold() == "all" or category.strip().casefold() == "all":
        raise ValueError("All-ward or all-category aggregation is refused")

    selected = [row for row in rows if row["ward"] == ward and row["category"] == category]
    if not selected:
        raise ValueError(f"No rows found for ward '{ward}' and category '{category}'")
    selected.sort(key=lambda row: row["period"])
    lag = 1 if growth_type == "MOM" else 12
    formula = "((current_actual_spend - prior_actual_spend) / prior_actual_spend) * 100"
    output: List[Dict[str, str]] = []
    for index, row in enumerate(selected):
        actual = row["actual_spend"].strip()
        result: Dict[str, str] = {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": actual,
            "growth_percent": "",
            "formula": formula,
            "status": "COMPUTED",
            "notes": row["notes"].strip(),
        }
        if not actual:
            result["status"] = "NULL_NOT_COMPUTED"
            result["formula"] = f"Not computed: actual_spend is NULL ({row['notes'].strip()})"
        elif index < lag:
            result["status"] = "INSUFFICIENT_HISTORY"
            result["formula"] = f"Not computed: no prior {growth_type} period"
        else:
            prior = selected[index - lag]["actual_spend"].strip()
            if not prior:
                result["status"] = "PRIOR_NULL_NOT_COMPUTED"
                result["formula"] = "Not computed: prior actual_spend is NULL"
            elif float(prior) == 0:
                result["status"] = "ZERO_BASE_NOT_COMPUTED"
                result["formula"] = "Not computed: prior actual_spend is zero"
            else:
                growth = (float(actual) - float(prior)) / float(prior) * 100
                result["growth_percent"] = f"{growth:.1f}%"
        output.append(result)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0C budget growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="One exact ward name")
    parser.add_argument("--category", required=True, help="One exact category name")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()
    rows, _ = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    with open(args.output, "w", newline="", encoding="utf-8") as output_file:
        fieldnames = ["period", "ward", "category", "actual_spend", "growth_percent", "formula", "status", "notes"]
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"Done. Growth results written to {args.output} ({len(results)} periods)")

if __name__ == "__main__":
    main()
