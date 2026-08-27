"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
from typing import Dict, List, Tuple


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def load_dataset(input_path: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    with open(input_path, "r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames or not REQUIRED_COLUMNS.issubset(set(reader.fieldnames)):
            raise ValueError("Dataset missing required columns.")

        rows = list(reader)

    null_rows = []
    for row in rows:
        if (row.get("actual_spend") or "").strip() == "":
            null_rows.append(
                {
                    "period": row.get("period", ""),
                    "ward": row.get("ward", ""),
                    "category": row.get("category", ""),
                    "notes": row.get("notes", ""),
                }
            )
    return rows, null_rows


def compute_growth(
    rows: List[Dict[str, str]],
    ward: str,
    category: str,
    growth_type: str,
) -> List[Dict[str, str]]:
    if not growth_type:
        raise ValueError("growth_type is required (MoM or YoY).")

    normalized_growth = growth_type.strip().upper()
    if normalized_growth not in {"MOM", "YOY"}:
        raise ValueError("growth_type must be MoM or YoY.")

    if ward.strip().lower() in {"all", "*"} or category.strip().lower() in {"all", "*"}:
        raise ValueError("Aggregation across wards/categories is not allowed.")

    scoped = [r for r in rows if r.get("ward") == ward and r.get("category") == category]
    scoped.sort(key=lambda item: item.get("period", ""))
    if not scoped:
        raise ValueError("No rows found for requested ward/category.")

    by_period = {row["period"]: row for row in scoped}
    output: List[Dict[str, str]] = []

    for idx, row in enumerate(scoped):
        period = row["period"]
        current_raw = (row.get("actual_spend") or "").strip()
        notes = (row.get("notes") or "").strip()

        out_row = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": current_raw,
            "growth_type": normalized_growth,
            "growth_percent": "",
            "formula": "",
            "null_flag": "",
            "null_reason": "",
        }

        if current_raw == "":
            out_row["formula"] = "N/A (actual_spend is null)"
            out_row["null_flag"] = "NEEDS_REVIEW"
            out_row["null_reason"] = notes or "Missing actual_spend"
            output.append(out_row)
            continue

        current_val = float(current_raw)
        baseline_val = None
        baseline_label = ""

        if normalized_growth == "MOM":
            if idx > 0:
                prev_raw = (scoped[idx - 1].get("actual_spend") or "").strip()
                if prev_raw:
                    baseline_val = float(prev_raw)
                    baseline_label = f"prev({scoped[idx - 1]['period']})"
        else:
            year, month = period.split("-")
            prior_period = f"{int(year) - 1}-{month}"
            prior = by_period.get(prior_period)
            if prior:
                prev_raw = (prior.get("actual_spend") or "").strip()
                if prev_raw:
                    baseline_val = float(prev_raw)
                    baseline_label = f"prev_year({prior_period})"

        if baseline_val is None:
            out_row["formula"] = "N/A (baseline unavailable)"
        elif baseline_val == 0:
            out_row["formula"] = "N/A (baseline is zero)"
            out_row["null_flag"] = "NEEDS_REVIEW"
            out_row["null_reason"] = "Cannot divide by zero baseline"
        else:
            growth = ((current_val - baseline_val) / baseline_val) * 100
            out_row["growth_percent"] = f"{growth:.1f}%"
            out_row["formula"] = (
                f"(({current_val:.1f} - {baseline_val:.1f}) / {baseline_val:.1f}) * 100 "
                f"[{baseline_label}]"
            )

        output.append(out_row)

    return output

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth output CSV")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    if null_rows:
        print(f"Detected {len(null_rows)} null actual_spend rows in dataset.")

    result = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "growth_percent",
        "formula",
        "null_flag",
        "null_reason",
    ]
    with open(args.output, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result)

    print(f"Done. Growth output written to {args.output}")

if __name__ == "__main__":
    main()
