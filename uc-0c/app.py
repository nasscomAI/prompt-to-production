"""
UC-0C app.py — Budget growth computation.
"""
import argparse
import csv
import os
import sys


EXPECTED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV is empty")

        actual_columns = {c.strip() for c in reader.fieldnames}
        missing = EXPECTED_COLUMNS - actual_columns
        if missing:
            raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")

        rows = []
        null_rows = []
        for idx, row in enumerate(reader, start=2):
            row = {k.strip(): v.strip() if v else "" for k, v in row.items()}
            rows.append(row)
            if not row.get("actual_spend"):
                reason = row.get("notes", "") or "No reason provided"
                null_rows.append((idx, row["period"], row["ward"], row["category"], reason))

    return {"columns": list(EXPECTED_COLUMNS), "rows": rows, "null_rows": null_rows}


def compute_growth(ward, category, growth_type, dataset):
    if growth_type not in ("MoM", "YoY"):
        raise ValueError("growth_type must be 'MoM' or 'YoY'")

    filtered = [r for r in dataset["rows"] if r["ward"] == ward and r["category"] == category]
    if not filtered:
        wards = sorted({r["ward"] for r in dataset["rows"]})
        cats = sorted({r["category"] for r in dataset["rows"]})
        raise ValueError(
            f"Ward '{ward}' or category '{category}' not found. "
            f"Available wards: {wards}, categories: {cats}"
        )

    filtered.sort(key=lambda r: r["period"])

    if len(filtered) < 2:
        raise ValueError("Need at least 2 periods to compute growth")

    result = []
    for idx, row in enumerate(filtered):
        entry = {
            "period": row["period"],
            "actual_spend": row["actual_spend"] if row["actual_spend"] else "",
            "previous_spend": "",
            "formula_string": "",
            "growth_value": "",
            "notes_flag": "",
        }

        if not row["actual_spend"]:
            reason = row.get("notes", "") or "No reason provided"
            entry["notes_flag"] = f"NULL - {reason}"
            result.append(entry)
            continue

        current = float(row["actual_spend"])

        if growth_type == "MoM":
            if idx == 0:
                entry["previous_spend"] = "N/A"
                entry["formula_string"] = "No previous period for MoM comparison"
                entry["growth_value"] = "N/A"
            else:
                prev_row = filtered[idx - 1]
                if not prev_row["actual_spend"]:
                    entry["previous_spend"] = "NULL"
                    entry["formula_string"] = "Cannot compute — previous period actual_spend is null"
                    entry["growth_value"] = "N/A"
                else:
                    prev = float(prev_row["actual_spend"])
                    growth = ((current - prev) / prev) * 100
                    entry["previous_spend"] = f"{prev:.1f}"
                    entry["formula_string"] = f"(({current:.1f} - {prev:.1f}) / {prev:.1f}) * 100"
                    entry["growth_value"] = f"{growth:+.1f}%"
        else:
            entry["previous_spend"] = "N/A"
            entry["formula_string"] = "No previous year data available (dataset only contains 2024)"
            entry["growth_value"] = "N/A"

        result.append(entry)

    return result


def main():
    parser = argparse.ArgumentParser(description="Compute budget growth for a ward and category.")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", default=None, help="Ward name (required)")
    parser.add_argument("--category", default=None, help="Category name (required)")
    parser.add_argument("--growth-type", default=None, choices=["MoM", "YoY"], help="Growth type: MoM or YoY (required)")
    parser.add_argument("--output", required=True, help="Output CSV path")

    args = parser.parse_args()

    if not args.growth_type:
        sys.exit("Error: --growth-type must be specified (MoM or YoY). Refusing to guess.")

    if not args.ward:
        sys.exit("Error: --ward must be specified. Aggregation across wards is not allowed.")

    if not args.category:
        sys.exit("Error: --category must be specified. Aggregation across categories is not allowed.")

    try:
        dataset = load_dataset(args.input)
    except (FileNotFoundError, ValueError) as e:
        sys.exit(f"Error loading dataset: {e}")

    if dataset["null_rows"]:
        print("Null actual_spend rows in dataset:")
        for idx, period, w, cat, reason in dataset["null_rows"]:
            print(f"  Row {idx}: {period}, {w}, {cat} — {reason}")

    try:
        growth_data = compute_growth(args.ward, args.category, args.growth_type, dataset)
    except ValueError as e:
        sys.exit(f"Error computing growth: {e}")

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["period", "actual_spend", "previous_spend", "formula_string", "growth_value", "notes_flag"]
        )
        writer.writeheader()
        writer.writerows(growth_data)

    print(f"Growth output written to {args.output}")


if __name__ == "__main__":
    main()
