"""
UC-0C — Monthly Growth Calculator
Computes per-period growth for one ward and one category while preserving null-row flags.
"""
import argparse
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
OUTPUT_COLUMNS = ["period", "ward", "category", "actual_spend", "growth_pct", "formula", "status", "null_reason"]


def load_dataset(input_path: str) -> List[Dict[str, str]]:
    with open(input_path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [col for col in REQUIRED_COLUMNS if col not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")
        return list(reader)


def _to_float(value: str) -> Optional[float]:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    return float(value)


def _format_percent(value: Optional[float]) -> str:
    if value is None:
        return ""
    return f"{value:+.1f}%"


def compute_growth(rows: List[Dict[str, str]], ward: str, category: str, growth_type: str) -> List[Dict[str, str]]:
    if growth_type != "MoM":
        raise ValueError("Only MoM growth is supported in this implementation.")

    filtered = [row for row in rows if row.get("ward") == ward and row.get("category") == category]
    filtered = sorted(filtered, key=lambda item: item.get("period", ""))

    if not filtered:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'.")

    results: List[Dict[str, str]] = []
    previous_value: Optional[float] = None
    previous_period: Optional[str] = None

    for row in filtered:
        period = row.get("period", "")
        actual_value = _to_float(row.get("actual_spend", ""))
        notes = (row.get("notes") or "").strip()

        if actual_value is None:
            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": "",
                    "growth_pct": "",
                    "formula": f"NULL actual spend; flagged from notes: {notes or 'no note'}",
                    "status": "NULL",
                    "null_reason": notes or "",
                }
            )
            previous_value = None
            previous_period = period
            continue

        if previous_value is None:
            formula = "n/a (baseline month; no prior month)"
            growth_pct = ""
            status = "BASELINE"
        else:
            if previous_value == 0:
                formula = f"growth not computed because previous month {previous_period} had zero actual spend"
                growth_pct = ""
                status = "SKIPPED"
            else:
                growth_value = ((actual_value - previous_value) / previous_value) * 100
                formula = f"({actual_value:.1f} - {previous_value:.1f}) / {previous_value:.1f} * 100"
                growth_pct = _format_percent(growth_value)
                status = "COMPUTED"

        results.append(
            {
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{actual_value:.1f}",
                "growth_pct": growth_pct,
                "formula": formula,
                "status": status,
                "null_reason": "",
            }
        )
        previous_value = actual_value
        previous_period = period

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0C growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward to analyze")
    parser.add_argument("--category", required=True, help="Category to analyze")
    parser.add_argument("--growth-type", required=True, help="Growth type; use MoM")
    parser.add_argument("--output", required=True, help="Path to write the growth CSV")
    args = parser.parse_args()

    if not args.growth_type:
        raise SystemExit("Refusing to guess growth type. Please specify --growth-type MoM.")

    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    output_path = Path(args.output)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(results)

    print(f"Growth output written to {output_path}")


if __name__ == "__main__":
    main()
