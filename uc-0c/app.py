"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv


def load_dataset(path):

    rows = []
    null_rows = []

    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)

        required = {
            "period",
            "ward",
            "category",
            "budgeted_amount",
            "actual_spend",
            "notes"
        }

        if not required.issubset(reader.fieldnames):
            raise ValueError("Dataset missing required columns")

        for r in reader:

            if r["actual_spend"] == "" or r["actual_spend"] is None:

                null_rows.append({
                    "period": r["period"],
                    "ward": r["ward"],
                    "category": r["category"],
                    "reason": r["notes"]
                })

            rows.append(r)

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):

    filtered = [
        r for r in rows
        if r["ward"] == ward and r["category"] == category
    ]

    filtered.sort(key=lambda x: x["period"])

    output = []

    previous = None

    for r in filtered:

        period = r["period"]
        spend = r["actual_spend"]

        if spend == "" or spend is None:

            output.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "NULL",
                "formula": f"NULL detected — reason: {r['notes']}"
            })

            previous = None
            continue

        spend = float(spend)

        if previous is None:

            output.append({
                "period": period,
                "actual_spend": spend,
                "growth": "N/A",
                "formula": "first period — no previous comparison"
            })

        else:

            growth = ((spend - previous) / previous) * 100

            output.append({
                "period": period,
                "actual_spend": spend,
                "growth": round(growth, 2),
                "formula": f"(({spend}-{previous})/{previous})*100"
            })

        previous = spend

    return output


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    if args.growth_type not in ["MoM", "YoY"]:
        raise ValueError("growth-type must be MoM or YoY")

    rows, null_rows = load_dataset(args.input)

    results = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type
    )

    with open(args.output, "w", newline='', encoding="utf-8") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=["period", "actual_spend", "growth", "formula"]
        )

        writer.writeheader()

        for r in results:
            writer.writerow(r)

    print("Growth analysis completed.")


if __name__ == "__main__":
    main()
