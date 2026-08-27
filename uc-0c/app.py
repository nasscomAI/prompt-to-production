"""
UC-0C — Budget Growth Calculator
"""
import argparse
import csv
import logging
import sys

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(file_path: str) -> list[dict]:
    with open(file_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    missing = [c for c in REQUIRED_COLUMNS if c not in rows[0]]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    null_rows = [(r["period"], r["ward"], r["category"], r["notes"])
                 for r in rows if not r.get("actual_spend", "").strip()]
    if null_rows:
        print(f"Warning: Found {len(null_rows)} rows with null actual_spend:", file=sys.stderr)
        for p, w, c, n in null_rows:
            print(f"  {p} | {w} | {c} | notes: {n}", file=sys.stderr)

    return rows


def compute_growth(data: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    if growth_type not in ("MoM", "YoY"):
        raise ValueError("growth_type must be 'MoM' or 'YoY'")

    filtered = [r for r in data if r["ward"] == ward and r["category"] == category]
    if not filtered:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'")

    filtered.sort(key=lambda r: r["period"])
    results = []

    for i, row in enumerate(filtered):
        actual = row.get("actual_spend", "").strip()
        if not actual:
            results.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": "",
                "prev_actual_spend": "",
                "growth_value": "N/A",
                "formula": f"{growth_type} not computed",
                "flag": f"NULL — {row['notes']}" if row['notes'] else "NULL — no reason given",
            })
            continue

        actual = float(actual)

        if growth_type == "MoM":
            prev = filtered[i - 1] if i > 0 else None
            prev_actual = prev.get("actual_spend", "").strip() if prev else ""
            formula = f"(current - previous) / previous * 100"
            if prev and prev_actual:
                prev_val = float(prev_actual)
                if prev_val == 0:
                    growth = "N/A (division by zero)"
                else:
                    growth = f"{((actual - prev_val) / prev_val * 100):.1f}%"
                results.append({
                    "period": row["period"],
                    "ward": ward,
                    "category": category,
                    "actual_spend": actual,
                    "prev_actual_spend": prev_val,
                    "growth_value": growth,
                    "formula": formula,
                    "flag": "",
                })
            else:
                results.append({
                    "period": row["period"],
                    "ward": ward,
                    "category": category,
                    "actual_spend": actual,
                    "prev_actual_spend": "",
                    "growth_value": "N/A (first period)",
                    "formula": formula,
                    "flag": "BASE_PERIOD",
                })
        elif growth_type == "YoY":
            prev_year = [r for r in filtered if r["period"].startswith(str(int(row["period"][:4]) - 1))
                         and r["period"][5:] == row["period"][5:]]
            formula = f"((current - previous_year) / previous_year) * 100"
            if prev_year:
                prev_val_str = prev_year[0].get("actual_spend", "").strip()
                if prev_val_str:
                    prev_val = float(prev_val_str)
                    if prev_val == 0:
                        growth = "N/A (division by zero)"
                    else:
                        growth = f"{((actual - prev_val) / prev_val * 100):.1f}%"
                    results.append({
                        "period": row["period"],
                        "ward": ward,
                        "category": category,
                        "actual_spend": actual,
                        "prev_actual_spend": prev_val,
                        "growth_value": growth,
                        "formula": formula,
                        "flag": "",
                    })
                else:
                    results.append({
                        "period": row["period"],
                        "ward": ward,
                        "category": category,
                        "actual_spend": actual,
                        "prev_actual_spend": "",
                        "growth_value": "N/A (null previous year)",
                        "formula": formula,
                        "flag": "NULL_PREV_YEAR",
                    })
            else:
                results.append({
                    "period": row["period"],
                    "ward": ward,
                    "category": category,
                    "actual_spend": actual,
                    "prev_actual_spend": "",
                    "growth_value": "N/A (no previous year data)",
                    "formula": formula,
                    "flag": "NO_PREV_YEAR",
                })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to filter")
    parser.add_argument("--category", required=True, help="Category to filter")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth type")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "actual_spend", "prev_actual_spend", "growth_value", "formula", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. {len(results)} rows written to {args.output}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()
