"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
from typing import Dict, List


REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def _to_float(value: str, column: str) -> float:
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"Invalid numeric value in {column}: {value!r}") from exc


def load_dataset(input_path: str) -> Dict[str, object]:
    """
    Read CSV, validate schema, parse rows, and report null actual_spend rows.
    """
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        missing_cols = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

        rows: List[Dict[str, object]] = []
        null_rows: List[Dict[str, str]] = []

        for idx, row in enumerate(reader, start=2):
            period = (row.get("period") or "").strip()
            ward = (row.get("ward") or "").strip()
            category = (row.get("category") or "").strip()
            notes = (row.get("notes") or "").strip()
            budgeted_raw = (row.get("budgeted_amount") or "").strip()
            actual_raw = (row.get("actual_spend") or "").strip()

            if len(period) != 7 or period[4] != "-":
                raise ValueError(f"Invalid period format at CSV line {idx}: {period!r}")

            budgeted_amount = _to_float(budgeted_raw, "budgeted_amount")
            actual_spend = None if actual_raw == "" else _to_float(actual_raw, "actual_spend")

            parsed = {
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted_amount,
                "actual_spend": actual_spend,
                "notes": notes,
            }
            rows.append(parsed)

            if actual_spend is None:
                null_rows.append(
                    {"period": period, "ward": ward, "category": category, "notes": notes}
                )

    return {"rows": rows, "null_count": len(null_rows), "null_rows": null_rows}


def compute_growth(
    dataset: Dict[str, object], ward: str, category: str, growth_type: str
) -> List[Dict[str, object]]:
    """
    Compute per-period growth rows for a specific ward + category.
    """
    if not growth_type:
        raise ValueError("growth_type is required (use MoM or YoY).")

    normalized_growth = growth_type.strip().upper()
    if normalized_growth not in {"MOM", "YOY"}:
        raise ValueError(f"Unsupported growth_type {growth_type!r}. Use MoM or YoY.")

    if ward.strip().lower() in {"any", "all", "*"} or category.strip().lower() in {"any", "all", "*"}:
        raise ValueError("Refusing aggregated request across wards/categories without explicit instruction.")

    rows = dataset["rows"]  # type: ignore[index]
    scoped = [
        r for r in rows  # type: ignore[union-attr]
        if r["ward"] == ward and r["category"] == category
    ]
    if not scoped:
        raise ValueError(f"No rows found for ward={ward!r} and category={category!r}.")

    scoped.sort(key=lambda r: r["period"])  # YYYY-MM lexical order is chronological

    result: List[Dict[str, object]] = []
    lag = 1 if normalized_growth == "MOM" else 12
    formula = (
        "((current_actual_spend - previous_actual_spend) / previous_actual_spend) * 100"
        if normalized_growth == "MOM"
        else "((current_actual_spend - actual_spend_12_months_ago) / actual_spend_12_months_ago) * 100"
    )

    for i, row in enumerate(scoped):
        current = row["actual_spend"]
        previous = scoped[i - lag]["actual_spend"] if i - lag >= 0 else None

        status = "COMPUTED"
        null_reason = ""
        growth_value = ""

        if current is None:
            status = "NOT_COMPUTED"
            null_reason = row["notes"] or "actual_spend is null"
        elif i - lag < 0:
            status = "NOT_COMPUTED"
            null_reason = "No prior period available for selected growth_type"
        elif previous is None:
            status = "NOT_COMPUTED"
            null_reason = scoped[i - lag]["notes"] or "prior actual_spend is null"
        elif previous == 0:
            status = "NOT_COMPUTED"
            null_reason = "prior actual_spend is zero; division undefined"
        else:
            growth = ((current - previous) / previous) * 100
            growth_value = f"{growth:.1f}%"

        result.append(
            {
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": "" if current is None else f"{current:.1f}",
                "growth_type": "MoM" if normalized_growth == "MOM" else "YoY",
                "formula": formula,
                "growth_value": growth_value,
                "status": status,
                "null_reason": null_reason,
            }
        )

    return result

def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to filter")
    parser.add_argument("--category", required=True, help="Category name to filter")
    parser.add_argument("--growth-type", required=True, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth output CSV")
    args = parser.parse_args()

    dataset = load_dataset(args.input)
    growth_rows = compute_growth(
        dataset=dataset,
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type,
    )

    output_fields = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "formula",
        "growth_value",
        "status",
        "null_reason",
    ]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(growth_rows)

    null_count = dataset["null_count"]  # type: ignore[index]
    print(f"Done. Wrote {len(growth_rows)} rows to {args.output}. Dataset null rows: {null_count}")

if __name__ == "__main__":
    main()
