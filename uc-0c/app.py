import argparse
import csv


def load_dataset(path):
    rows = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        required = ["period","ward","category","budgeted_amount","actual_spend","notes"]

        for col in required:
            if col not in reader.fieldnames:
                raise ValueError("Missing required column: " + col)

        for r in reader:
            rows.append(r)

    return rows


def compute_growth(rows, ward, category):

    filtered = [
        r for r in rows
        if r["ward"] == ward and r["category"] == category
    ]

    filtered.sort(key=lambda x: x["period"])

    output = []

    prev = None

    for r in filtered:

        spend = r["actual_spend"]

        if spend == "" or spend is None:
            output.append({
                "period": r["period"],
                "actual_spend": "NULL",
                "growth": "NULL",
                "formula": "NULL actual_spend",
                "note": r["notes"]
            })
            prev = None
            continue

        spend = float(spend)

        if prev is None:
            growth = ""
            formula = ""
        else:
            growth_val = ((spend - prev) / prev) * 100
            growth = f"{growth_val:.2f}%"
            formula = f"(({spend} - {prev}) / {prev}) * 100"

        output.append({
            "period": r["period"],
            "actual_spend": spend,
            "growth": growth,
            "formula": formula,
            "note": r["notes"]
        })

        prev = spend

    return output


def main():

    parser = argparse.ArgumentParser(description="UC-0C Budget Growth")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    if args.growth_type != "MoM":
        raise ValueError("Only MoM growth supported")

    rows = load_dataset(args.input)

    result = compute_growth(rows, args.ward, args.category)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["period","actual_spend","growth","formula","note"]
        )

        writer.writeheader()
        writer.writerows(result)

    print("Growth table written to", args.output)


if __name__ == "__main__":
    main()