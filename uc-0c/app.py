"""
UC-0C app.py — Number That Looks Right
"""
import argparse
import csv
import sys

def main():
    parser = argparse.ArgumentParser(description="Compute MoM growth")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward")
    parser.add_argument("--category")
    parser.add_argument("--growth-type")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    if not args.growth_type:
        print("ERROR: --growth-type must be specified (e.g. MoM). Refusing to guess.")
        sys.exit(1)
        
    if not args.ward or not args.category:
        print("ERROR: Aggregation across wards or categories without explicit instructions is refused.")
        sys.exit(1)

    with open(args.input, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Filter and sort
    filtered_rows = [r for r in rows if r["ward"] == args.ward and r["category"] == args.category]
    filtered_rows.sort(key=lambda x: x["period"])

    output_rows = []
    prev_spend = None

    for r in filtered_rows:
        period = r["period"]
        actual_str = r["actual_spend"].strip()
        notes = r["notes"].strip()
        
        out = {
            "period": period,
            "ward": r["ward"],
            "category": r["category"],
            "actual_spend": actual_str if actual_str else "NULL",
            "growth": "",
            "formula": "",
            "flag": ""
        }

        if not actual_str:
            out["flag"] = f"NULL value detected. Reason: {notes}"
            out["growth"] = "N/A"
            out["formula"] = "N/A (Null value)"
            prev_spend = None
        else:
            actual = float(actual_str)
            if prev_spend is not None:
                growth = ((actual - prev_spend) / prev_spend) * 100
                out["growth"] = f"{growth:+.1f}%"
                out["formula"] = f"({actual} - {prev_spend}) / {prev_spend}"
            else:
                out["growth"] = "N/A"
                out["formula"] = "N/A (No previous month data)"
            prev_spend = actual

        output_rows.append(out)

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["period", "ward", "category", "actual_spend", "growth", "formula", "flag"])
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Done. Output written to {args.output}")

if __name__ == "__main__":
    main()
