"""
UC-0C — Number That Looks Right
Implements load_dataset and compute_growth per agents.md and skills.md.
"""
import argparse
import csv
import sys
from pathlib import Path

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]

MOM_FORMULA = "(actual_spend[t] - actual_spend[t-1]) / actual_spend[t-1] * 100"


def _is_blank(value) -> bool:
    return value is None or str(value).strip() == ""


def _parse_spend(value):
    if _is_blank(value):
        return None
    try:
        return float(str(value).strip())
    except ValueError:
        return None


def load_dataset(input_path: str):
    """Read CSV, validate columns, report null count and which rows before returning."""
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [col for col in REQUIRED_COLUMNS if col not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")
        rows = list(reader)

    null_rows = []
    for row in rows:
        spend = _parse_spend(row.get("actual_spend"))
        row["_actual_spend"] = spend
        if spend is None:
            null_rows.append(
                {
                    "period": row.get("period", ""),
                    "ward": row.get("ward", ""),
                    "category": row.get("category", ""),
                    "notes": (row.get("notes") or "").strip(),
                }
            )

    print(f"Loaded {len(rows)} rows from {input_path}")
    print(f"Null actual_spend rows: {len(null_rows)}")
    for item in null_rows:
        reason = item["notes"] or "notes column empty"
        print(
            f"  NULL {item['period']} | {item['ward']} | {item['category']} | reason: {reason}"
        )
    return rows, null_rows


def _refuses_aggregation(ward: str, category: str) -> str:
    combined = f"{ward} {category}".lower()
    all_ward_markers = ["all ward", "all wards", "city total", "all-ward", "across ward"]
    all_cat_markers = ["all categor", "all categories", "combined"]
    if not ward or any(marker in ward.lower() for marker in all_ward_markers) or any(
        marker in combined for marker in all_ward_markers
    ):
        return (
            "REFUSED: never aggregate across wards. Provide one exact --ward value "
            "(for example 'Ward 1 – Kasba')."
        )
    if not category or any(marker in category.lower() for marker in all_cat_markers):
        return (
            "REFUSED: never aggregate across categories. Provide one exact --category value "
            "(for example 'Roads & Pothole Repair')."
        )
    return ""


def compute_growth(rows, ward: str, category: str, growth_type: str, output_path: str):
    """Return per-period table with formula shown. Null rows are flagged, not computed."""
    if _is_blank(growth_type):
        raise ValueError(
            "REFUSED: --growth-type was not specified. Provide an explicit type such as MoM. "
            "Do not guess MoM or YoY."
        )

    refusal = _refuses_aggregation(ward, category)
    if refusal:
        raise ValueError(refusal)

    growth_type_normalised = growth_type.strip()
    if growth_type_normalised.lower() != "mom":
        raise ValueError(
            f"REFUSED: unsupported --growth-type '{growth_type}'. "
            "This calculator only runs when growth type is explicitly MoM."
        )

    scoped = [
        row
        for row in rows
        if (row.get("ward") or "").strip() == ward.strip()
        and (row.get("category") or "").strip() == category.strip()
    ]
    if not scoped:
        raise ValueError(
            f"REFUSED: no rows found for ward '{ward}' and category '{category}'. "
            "Check exact spelling including the en-dash in ward names."
        )

    scoped.sort(key=lambda row: row.get("period") or "")
    output_rows = []
    previous_spend = None

    for row in scoped:
        spend = row.get("_actual_spend")
        notes = (row.get("notes") or "").strip()
        is_null = spend is None
        growth_pct = ""
        formula = MOM_FORMULA

        if is_null:
            null_flag = "NULL"
            null_reason = notes or "actual_spend blank; reason not provided in notes"
            growth_pct = ""
        elif previous_spend in (None, 0):
            null_flag = ""
            null_reason = ""
            growth_pct = ""
            formula = MOM_FORMULA + " ; first usable period or previous spend is zero so MoM is not computed"
        else:
            null_flag = ""
            null_reason = ""
            change = (spend - previous_spend) / previous_spend * 100
            growth_pct = f"{change:+.1f}%"

        output_rows.append(
            {
                "period": row.get("period", ""),
                "ward": ward,
                "category": category,
                "actual_spend": "" if is_null else f"{spend:.1f}",
                "previous_spend": "" if previous_spend is None else f"{previous_spend:.1f}",
                "growth_pct": growth_pct,
                "growth_type": "MoM",
                "formula": formula,
                "null_flag": null_flag,
                "null_reason": null_reason,
            }
        )
        if not is_null:
            previous_spend = spend

    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "previous_spend",
        "growth_pct",
        "growth_type",
        "formula",
        "null_flag",
        "null_reason",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C ward-level MoM growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", default="", help="Exact ward name")
    parser.add_argument("--category", default="", help="Exact category name")
    parser.add_argument("--growth-type", dest="growth_type", default="", help="Required growth type, e.g. MoM")
    parser.add_argument("--output", required=True, help="Path to growth_output.csv")
    args = parser.parse_args()

    try:
        rows, _null_rows = load_dataset(args.input)
        compute_growth(rows, args.ward, args.category, args.growth_type, args.output)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    print(f"Done. Per-ward per-category table written to {args.output}")


if __name__ == "__main__":
    main()
