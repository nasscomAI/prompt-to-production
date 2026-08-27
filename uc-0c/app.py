"""
UC-0C — Number That Looks Right
"""
import argparse
import csv


def load_dataset(filepath: str) -> dict:
    required = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    rows = []
    null_rows = []

    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV file is empty or has no header.")
        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

        for row in reader:
            rows.append(row)
            if not row["actual_spend"].strip():
                null_rows.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "notes": row["notes"],
                })

    return {"data": rows, "null_rows": null_rows}


def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    if growth_type not in ("MoM", "YoY"):
        raise ValueError("--growth-type must be 'MoM' or 'YoY'. Got: " + growth_type)

    filtered = [r for r in data if r["ward"] == ward and r["category"] == category]
    if not filtered:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'.")

    filtered.sort(key=lambda r: r["period"])
    years = set(r["period"][:4] for r in filtered)

    if growth_type == "YoY" and len(years) < 2:
        raise ValueError(
            "YoY growth requires data spanning at least 2 years. "
            f"Available years: {', '.join(sorted(years))}."
        )

    formula = {
        "MoM": "((current_spend - previous_spend) / previous_spend) * 100",
        "YoY": "((current_spend - year_ago_spend) / year_ago_spend) * 100",
    }[growth_type]

    result = []
    prev = None

    for i, row in enumerate(filtered):
        entry = {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": row["actual_spend"],
            "growth": "",
            "formula": "",
            "null_flag": "",
        }

        if not row["actual_spend"].strip():
            entry["actual_spend"] = ""
            entry["growth"] = "N/A"
            entry["formula"] = ""
            entry["null_flag"] = f"Not computed — {row['notes']}"
            result.append(entry)
            prev = None
            continue

        current = float(row["actual_spend"])

        if growth_type == "MoM":
            if prev is not None:
                if prev == 0:
                    entry["growth"] = "N/A (division by zero)"
                    entry["formula"] = formula
                else:
                    pct = ((current - prev) / prev) * 100
                    entry["growth"] = f"{pct:+.1f}%"
                    entry["formula"] = formula
            else:
                entry["growth"] = "N/A (first period)"
                entry["formula"] = ""

        elif growth_type == "YoY":
            prev_year_row = None
            for j in range(i - 12, -1, -1):
                if (filtered[j]["period"][:4] == str(int(row["period"][:4]) - 1)
                        and filtered[j]["period"][5:] == row["period"][5:]):
                    prev_year_row = filtered[j]
                    break
            if prev_year_row and prev_year_row["actual_spend"].strip():
                prev_val = float(prev_year_row["actual_spend"])
                if prev_val == 0:
                    entry["growth"] = "N/A (division by zero)"
                    entry["formula"] = formula
                else:
                    pct = ((current - prev_val) / prev_val) * 100
                    entry["growth"] = f"{pct:+.1f}%"
                    entry["formula"] = formula
            else:
                entry["growth"] = "N/A (no prior year data)"
                entry["formula"] = ""

        result.append(entry)

        if row["actual_spend"].strip():
            prev = current

    return result


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    dataset = load_dataset(args.input)

    nulls = dataset["null_rows"]
    if nulls:
        print(f"Found {len(nulls)} row(s) with null actual_spend:")
        for n in nulls:
            print(f"  {n['period']} | {n['ward']} | {n['category']} | {n['notes']}")

    results = compute_growth(dataset["data"], args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "null_flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth results written to {args.output}")


if __name__ == "__main__":
    main()
