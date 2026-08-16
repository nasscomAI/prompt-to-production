import argparse
import csv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    if args.growth_type != "MoM":
        raise ValueError("Unsupported growth type. Only MoM is supported.")

    with open(args.input, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    required = {
        "period", "ward", "category",
        "budgeted_amount", "actual_spend", "notes"
    }

    if not required.issubset(rows[0].keys()):
        raise ValueError("Required columns are missing.")

    selected = [
        r for r in rows
        if r["ward"] == args.ward and r["category"] == args.category
    ]

    selected.sort(key=lambda r: r["period"])

    output = []

    previous = None

    for r in selected:
        spend = r["actual_spend"]

        if spend == "":
            output.append({
                "period": r["period"],
                "actual_spend": "",
                "formula": "NOT COMPUTED",
                "growth": "NULL",
                "status": "FLAGGED: " + r["notes"]
            })
            previous = None
            continue

        current = float(spend)

        if previous is None:
            growth = ""
            formula = "N/A (first available period)"
        else:
            growth = f"{((current - previous) / previous) * 100:.1f}%"
            formula = f"(({current} - {previous}) / {previous}) * 100"

        output.append({
            "period": r["period"],
            "actual_spend": spend,
            "formula": formula,
            "growth": growth,
            "status": ""
        })

        previous = current

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["period", "actual_spend", "formula", "growth", "status"]
        )
        writer.writeheader()
        writer.writerows(output)

    print(f"Growth results written to {args.output}")


if __name__ == "__main__":
    main()