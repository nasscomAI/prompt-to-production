import argparse
import csv


def load_dataset(path):
    rows = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        required = ["period","ward","category","budgeted_amount","actual_spend","notes"]

        for col in required:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing column: {col}")

        for r in reader:
            rows.append(r)

    return rows


def compute_growth(rows, ward, category, growth_type):

    if growth_type != "MoM":
        raise ValueError("Only MoM growth supported for this task.")

    filtered = [
        r for r in rows
        if r["ward"] == ward and r["category"] == category
    ]

    filtered.sort(key=lambda x: x["period"])

    results = []
    prev = None

    for r in filtered:

        spend = r["actual_spend"]

        if spend == "" or spend is None:
            results.append({
                "period": r["period"],
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth_percent": "",
                "formula": "",
                "flag": f"NULL actual_spend – {r['notes']}"
            })
            prev = None
            continue

        spend = float(spend)

        if prev is None:
            results.append({
                "period": r["period"],
                "ward": ward,
                "category": category,
                "actual_spend": spend,
                "growth_percent": "",
                "formula": "No previous month",
                "flag": ""
            })
        else:
            growth = ((spend - prev) / prev) * 100

            results.append({
                "period": r["period"],
                "ward": ward,
                "category": category,
                "actual_spend": spend,
                "growth_percent": round(growth,1),
                "formula": "(current-prev)/prev *100",
                "flag": ""
            })

        prev = spend

    return results


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    rows = load_dataset(args.input)

    results = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type
    )

    fieldnames = [
        "period","ward","category",
        "actual_spend","growth_percent","formula","flag"
    ]

    with open(args.output,"w",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f,fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print("Growth output written to", args.output)


if __name__ == "__main__":
    main()