"""
UC-0C growth calculator.
"""
import argparse
import csv

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(path: str):
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header row")

        missing = REQUIRED_COLUMNS.difference(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

        rows = list(reader)

    null_rows = [row for row in rows if not (row.get("actual_spend") or "").strip()]
    return rows, null_rows


def compute_growth(rows, ward: str, category: str, growth_type: str):
    if not growth_type:
        raise ValueError("growth type is required")
    if growth_type != "MoM":
        raise ValueError("Only MoM growth is supported for this UC")
    if not ward or ward.lower() == "all":
        raise ValueError("Refusing all-ward aggregation")
    if not category or category.lower() == "all":
        raise ValueError("Refusing all-category aggregation")

    filtered = [
        row for row in rows if row["ward"] == ward and row["category"] == category
    ]
    filtered.sort(key=lambda row: row["period"])

    output = []
    previous_actual = None
    for row in filtered:
        actual_text = (row.get("actual_spend") or "").strip()
        formula = "(current_actual - previous_actual) / previous_actual * 100"
        if not actual_text:
            growth = "NULL"
            note = row.get("notes") or "Null actual_spend"
            previous_actual = None
        else:
            actual_value = float(actual_text)
            if previous_actual in (None, 0):
                growth = "N/A"
                note = "No prior comparable month"
            else:
                growth_value = ((actual_value - previous_actual) / previous_actual) * 100
                growth = f"{growth_value:+.1f}%"
                note = ""
            previous_actual = actual_value

        output.append(
            {
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": actual_text or "NULL",
                "growth_type": growth_type,
                "growth_result": growth,
                "formula": formula,
                "note": note,
            }
        )

    return output


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward budget CSV")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, help="Growth type")
    parser.add_argument("--output", required=True, help="Path to write CSV output")
    args = parser.parse_args()

    rows, _null_rows = load_dataset(args.input)
    output_rows = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "actual_spend", "growth_type", "growth_result", "formula", "note"]
    with open(args.output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
