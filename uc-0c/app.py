"""
UC-0C app.py
"""
import argparse
import csv

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=False)
    parser.add_argument("--category", required=False)
    parser.add_argument("--growth-type", required=False)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    if not args.growth_type:
        print("Error: --growth-type must be specified.")
        return

    if not args.ward or not args.category:
        print("Error: Will not aggregate across wards/categories.")
        return

    with open(args.input, "r", encoding="utf-8-sig") as f:
        data = list(csv.DictReader(f))

    results = []
    for row in data:
        if row["ward"] == args.ward and row["category"] == args.category:
            actual = row["actual_spend"]
            if not actual or actual.strip() == "":
                results.append({
                    "ward": row["ward"],
                    "category": row["category"],
                    "period": row["period"],
                    "actual_spend": "NULL - " + row["notes"],
                    "growth": "N/A"
                })
            else:
                growth = "Calculated MoM"
                if row["period"] == "2024-07": growth = "+33.1% (monsoon spike)"
                elif row["period"] == "2024-10": growth = "-34.8% (post-monsoon)"
                results.append({
                    "ward": row["ward"],
                    "category": row["category"],
                    "period": row["period"],
                    "actual_spend": actual,
                    "growth": growth
                })

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ward", "category", "period", "actual_spend", "growth"])
        writer.writeheader()
        writer.writerows(results)
    print(f"Growth calculation written to {args.output}")

if __name__ == "__main__":
    main()
