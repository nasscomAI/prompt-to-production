import argparse
import csv


def load_dataset(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def compute_growth(rows, ward, category):

    # Normalize dash types
    ward = ward.replace("–", "-")

    filtered = [
        r for r in rows
        if r["ward"].replace("–", "-") == ward
        and r["category"] == category
    ]

    # Sort by period
    filtered.sort(key=lambda x: x["period"])

    output = []
    prev_value = None

    for r in filtered:

        period = r["period"]
        spend = r["actual_spend"]

        # Handle NULL spend
        if spend == "":
            output.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "FLAGGED_NULL",
                "formula": "N/A",
                "notes": r["notes"]
            })
            prev_value = None
            continue

        spend = float(spend)

        if prev_value is None:

            output.append({
                "period": period,
                "actual_spend": spend,
                "growth": "N/A",
                "formula": "No previous value",
                "notes": r["notes"]
            })

        else:

            growth = 0

            if prev_value != 0:
                growth = ((spend - prev_value) / prev_value) * 100

            output.append({
                "period": period,
                "actual_spend": spend,
                "growth": growth,
                "formula": f"(({spend}-{prev_value})/{prev_value})*100",
                "notes": r["notes"]
            })

        prev_value = spend

    return output


def main():

    parser = argparse.ArgumentParser(description="Budget Growth Calculator")

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    rows = load_dataset(args.input)

    results = compute_growth(rows, args.ward, args.category)

    with open(args.output, "w", newline="", encoding="utf-8") as f:

        fieldnames = ["period", "actual_spend", "growth", "formula", "notes"]

        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

    print("Output written to:", args.output)


if __name__ == "__main__":
    main()