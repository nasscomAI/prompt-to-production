import argparse
import csv


def load_dataset(path):
    data = []
    null_rows = []

    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        required = ["period", "ward", "category", "actual_spend", "notes"]
        for col in required:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing column: {col}")

        for row in reader:
            if row["actual_spend"] == "" or row["actual_spend"] is None:
                null_rows.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "reason": row["notes"]
                })
            data.append(row)

    return data, null_rows


def validate_inputs(data, ward, category):
    wards = set(row["ward"] for row in data)
    categories = set(row["category"] for row in data)

    if ward not in wards:
        raise ValueError(f"Invalid ward: {ward}")

    if category not in categories:
        raise ValueError(f"Invalid category: {category}")


def compute_growth(data, ward, category, growth_type):
    filtered = [
        row for row in data
        if row["ward"] == ward and row["category"] == category
    ]

    filtered.sort(key=lambda x: x["period"])

    results = []

    for i in range(len(filtered)):
        row = filtered[i]
        period = row["period"]
        current = row["actual_spend"]

        # --- NULL CASE ---
        if current == "" or current is None:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "NA",
                "formula": "NA",
                "data_status": "NULL",
                "flag": f"NULL: {row['notes']}"
            })
            continue

        current = float(current)

        # --- FIRST ROW ---
        if i == 0:
            results.append({
                "period": period,
                "actual_spend": current,
                "growth": "NA",
                "formula": "NA (no previous period)",
                "data_status": "VALID",
                "flag": ""
            })
            continue

        prev = filtered[i - 1]["actual_spend"]

        # --- PREVIOUS NULL ---
        if prev == "" or prev is None:
            results.append({
                "period": period,
                "actual_spend": current,
                "growth": "NA",
                "formula": "Previous value NULL",
                "data_status": "PARTIAL",
                "flag": "NEEDS_REVIEW"
            })
            continue

        prev = float(prev)

        # --- GROWTH CALC ---
        if growth_type == "MoM":
            growth = ((current - prev) / prev) * 100
            formula = f"MoM = (({current} - {prev}) / {prev}) * 100"
        else:
            raise ValueError("Only MoM supported")

        results.append({
            "period": period,
            "actual_spend": current,
            "growth": f"{growth:.1f}%",
            "formula": formula,
            "data_status": "VALID",
            "flag": ""
        })

    return results


def write_output(results, output_path):
    with open(output_path, "w", newline='', encoding='utf-8') as f:
        fieldnames = [
            "period", "actual_spend", "growth",
            "formula", "data_status", "flag"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    # --- LOAD ---
    data, nulls = load_dataset(args.input)

    # --- AUDIT REPORT ---
    print("\n=== DATA AUDIT REPORT ===")
    print(f"Total NULL rows: {len(nulls)}")

    for n in nulls:
        print(f"{n['period']} | {n['ward']} | {n['category']} → {n['reason']}")

    # --- VALIDATE ---
    validate_inputs(data, args.ward, args.category)

    # --- COMPUTE ---
    results = compute_growth(data, args.ward, args.category, args.growth_type)

    # --- WRITE ---
    write_output(results, args.output)

    print(f"\nOutput written to: {args.output}")


if __name__ == "__main__":
    main()