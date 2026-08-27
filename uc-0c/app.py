"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def to_float(value: str):
    if value is None:
        return None
    value = str(value).strip()
    if value == "":
        return None
    return float(value)


def load_dataset(input_path: str):
    with open(input_path, "r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
            raise ValueError("Input CSV has no header row.")

        missing = REQUIRED_COLUMNS.difference(set(reader.fieldnames))
        if missing:
            missing_list = ", ".join(sorted(missing))
            raise ValueError(f"Input CSV missing required columns: {missing_list}")

        rows = list(reader)

    null_rows = []
    for row in rows:
        if to_float(row.get("actual_spend", "")) is None:
            null_rows.append(
                {
                    "period": row.get("period", ""),
                    "ward": row.get("ward", ""),
                    "category": row.get("category", ""),
                    "notes": row.get("notes", ""),
                }
            )

    return rows, null_rows


def compute_growth(rows, ward: str, category: str, growth_type: str):
    if growth_type not in {"MoM", "YoY"}:
        raise ValueError("--growth-type must be either MoM or YoY.")

    if ward.strip().lower() in {"all", "any", "*"} or category.strip().lower() in {"all", "any", "*"}:
        raise ValueError("Aggregation across wards/categories is not allowed. Provide one exact ward and one exact category.")

    selected = [
        row for row in rows if row.get("ward", "").strip() == ward.strip() and row.get("category", "").strip() == category.strip()
    ]

    if not selected:
        raise ValueError("No rows found for the given ward and category.")

    selected.sort(key=lambda r: r.get("period", ""))

    computed = []
    for i, row in enumerate(selected):
        current = to_float(row.get("actual_spend", ""))
        notes = (row.get("notes", "") or "").strip()

        out = {
            "period": row.get("period", ""),
            "ward": row.get("ward", ""),
            "category": row.get("category", ""),
            "actual_spend": "" if current is None else f"{current:.1f}",
            "growth_type": growth_type,
            "growth_percent": "",
            "formula": "",
            "status": "",
            "null_reason": "",
        }

        if current is None:
            out["status"] = "NULL_ACTUAL_SPEND"
            out["null_reason"] = notes or "Missing value"
            computed.append(out)
            continue

        if growth_type == "MoM":
            if i == 0:
                out["status"] = "NO_PREVIOUS_PERIOD"
                out["formula"] = "MoM = (current - previous) / previous * 100"
                computed.append(out)
                continue

            previous = to_float(selected[i - 1].get("actual_spend", ""))
            if previous is None:
                out["status"] = "PREVIOUS_VALUE_MISSING"
                out["formula"] = "MoM = (current - previous) / previous * 100"
                out["null_reason"] = (selected[i - 1].get("notes", "") or "").strip() or "Previous month missing value"
                computed.append(out)
                continue

            if previous == 0:
                out["status"] = "PREVIOUS_VALUE_ZERO"
                out["formula"] = "MoM = (current - previous) / previous * 100"
                computed.append(out)
                continue

            growth = ((current - previous) / previous) * 100
            out["growth_percent"] = f"{growth:.1f}"
            out["formula"] = f"(({current:.1f} - {previous:.1f}) / {previous:.1f}) * 100"
            out["status"] = "OK"
            computed.append(out)
            continue

        # YoY path kept explicit for enforcement if future annual datasets are used.
        matching_prev_year = None
        year, month = row.get("period", "").split("-")
        previous_year_period = f"{int(year) - 1:04d}-{month}"
        for candidate in selected:
            if candidate.get("period", "") == previous_year_period:
                matching_prev_year = candidate
                break

        out["formula"] = "YoY = (current - same_month_last_year) / same_month_last_year * 100"
        if matching_prev_year is None:
            out["status"] = "PREVIOUS_YEAR_MISSING"
            computed.append(out)
            continue

        previous_year_value = to_float(matching_prev_year.get("actual_spend", ""))
        if previous_year_value is None:
            out["status"] = "PREVIOUS_YEAR_VALUE_MISSING"
            out["null_reason"] = (matching_prev_year.get("notes", "") or "").strip() or "Previous year same month missing value"
            computed.append(out)
            continue

        if previous_year_value == 0:
            out["status"] = "PREVIOUS_YEAR_VALUE_ZERO"
            computed.append(out)
            continue

        growth = ((current - previous_year_value) / previous_year_value) * 100
        out["growth_percent"] = f"{growth:.1f}"
        out["formula"] = f"(({current:.1f} - {previous_year_value:.1f}) / {previous_year_value:.1f}) * 100"
        out["status"] = "OK"
        computed.append(out)

    return computed


def write_output(output_path: str, rows):
    fields = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "growth_percent",
        "formula",
        "status",
        "null_reason",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    print(f"Detected {len(null_rows)} rows with null actual_spend values.")
    for nr in null_rows:
        print(f"NULL -> {nr['period']} | {nr['ward']} | {nr['category']} | reason: {nr['notes']}")

    computed_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_output(args.output, computed_rows)
    print(f"Done. Growth output written to {args.output}")

if __name__ == "__main__":
    main()
