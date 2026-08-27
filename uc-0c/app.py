import csv
import os
from collections import defaultdict

INPUT_PATH  = os.path.join("data", "budget", "ward_budget.csv")
OUTPUT_PATH = "growth_output.csv"
ANOMALY_PATH = "anomaly_report.txt"

def load_budget_data(path: str) -> list[dict]:
    rows = []
    skipped = 0

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        print(f"[INFO] Columns detected: {reader.fieldnames}")
        print(f"[INFO] Loading data from: {path}")

        for i, row in enumerate(reader, start=2):
            try:
                year = int(row["period"].split("-")[0])

                rows.append({
                    "ward":     row["ward"].strip(),
                    "category": row["category"].strip(),
                    "year":     year,
                    "amount":   float(row["actual_spend"]),
                })

            except Exception as e:
                print(f"[WARN] Skipping row {i}: {e}")
                skipped += 1

    print(f"[INFO] Loaded {len(rows)} rows. Skipped {skipped} invalid rows.")
    return rows


def group_by_ward_category(rows: list[dict]) -> dict:
    data = defaultdict(lambda: defaultdict(dict))
    for row in rows:
        data[row["ward"]][row["category"]][row["year"]] = row["amount"]
    return data


def compute_growth(year_amounts: dict) -> dict:
    sorted_years = sorted(year_amounts.keys())

    if len(sorted_years) == 1:
        yr = sorted_years[0]
        return {
            "year_current": yr,
            "amount_current": year_amounts[yr],
            "year_previous": None,
            "amount_previous": None,
            "growth_rate_pct": None,
            "flag": "MISSING_YEAR"
        }

    yr_prev, yr_curr = sorted_years[-2], sorted_years[-1]
    amt_prev, amt_curr = year_amounts[yr_prev], year_amounts[yr_curr]

    growth = None if amt_prev == 0 else ((amt_curr - amt_prev) / amt_prev) * 100

    return {
        "year_current": yr_curr,
        "amount_current": amt_curr,
        "year_previous": yr_prev,
        "amount_previous": amt_prev,
        "growth_rate_pct": growth,
        "flag": None
    }


def write_output(results, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)


def main():
    rows = load_budget_data(INPUT_PATH)
    grouped = group_by_ward_category(rows)

    results = []
    for ward, cats in grouped.items():
        for cat, years in cats.items():
            r = compute_growth(years)
            r["ward"] = ward
            r["category"] = cat
            results.append(r)

    write_output(results, OUTPUT_PATH)
    print("✅ Done")


if __name__ == "__main__":
    main()


