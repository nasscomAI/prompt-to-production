"""
UC-0C — Number That Looks Right
Built from agents.md / skills.md (RICE enforcement, CRAFT-tested).
"""
import argparse
import csv
import sys
from pathlib import Path

REQUIRED_COLUMNS = (
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
)
ALLOWED_GROWTH = ("MoM", "YoY")
MOM_FORMULA = "(actual_t - actual_t-1) / actual_t-1 * 100"
YOY_FORMULA = "(actual_t - actual_t-12) / actual_t-12 * 100"
OUTPUT_FIELDS = (
    "period",
    "ward",
    "category",
    "actual_spend",
    "growth_pct",
    "formula",
    "status",
    "notes",
)


class RefusalError(ValueError):
    """Raised when the tool must stop instead of guessing."""


def _is_blank(value) -> bool:
    return value is None or str(value).strip() == ""


def _parse_spend(value):
    if _is_blank(value):
        return None
    return float(str(value).strip())


def _normalize_dash(value: str) -> str:
    return (value or "").replace("\u2013", "-").replace("\u2014", "-").strip()


def _looks_like_all(value: str) -> bool:
    token = _normalize_dash(value).lower()
    return token in {"", "all", "all wards", "city", "*"}


def load_dataset(input_path: str) -> dict:
    """Read CSV, validate columns, report nulls before returning rows."""
    with open(input_path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header row.")
        missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        rows = []
        null_report = []
        for raw in reader:
            spend = _parse_spend(raw.get("actual_spend"))
            row = {
                "period": (raw.get("period") or "").strip(),
                "ward": (raw.get("ward") or "").strip(),
                "category": (raw.get("category") or "").strip(),
                "budgeted_amount": _parse_spend(raw.get("budgeted_amount")),
                "actual_spend": spend,
                "notes": (raw.get("notes") or "").strip(),
            }
            rows.append(row)
            if spend is None:
                null_report.append(
                    {
                        "period": row["period"],
                        "ward": row["ward"],
                        "category": row["category"],
                        "notes": row["notes"] or "(no notes provided)",
                    }
                )

    return {"rows": rows, "null_report": null_report, "null_count": len(null_report)}


def _print_null_report(dataset: dict) -> None:
    print("NULL REPORT (before any growth computation)")
    print(f"null actual_spend rows: {dataset['null_count']}")
    for item in dataset["null_report"]:
        print(
            f"  {item['period']} | {item['ward']} | {item['category']} | "
            f"reason: {item['notes']}"
        )


def _format_pct(value: float) -> str:
    rounded = round(value, 1)
    return f"{rounded:+.1f}%"


def _format_spend(value) -> str:
    if value is None:
        return "NULL"
    return str(value)


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str) -> list:
    """Per-period table for one ward and one category; formula on every row."""
    if _looks_like_all(ward) or _looks_like_all(category):
        raise RefusalError(
            "REFUSAL: all-ward or all-category aggregation is not allowed. "
            "Pass exactly one --ward and one --category from the dataset."
        )
    if not growth_type:
        raise RefusalError(
            "REFUSAL: --growth-type is required. Specify MoM or YoY. "
            "The system will not guess the formula."
        )
    if growth_type not in ALLOWED_GROWTH:
        raise RefusalError(
            f"REFUSAL: unknown growth-type '{growth_type}'. Allowed: MoM, YoY."
        )

    rows = dataset["rows"]
    wards = sorted({r["ward"] for r in rows})
    categories = sorted({r["category"] for r in rows})
    ward_map = {_normalize_dash(w): w for w in wards}
    category_map = {_normalize_dash(c): c for c in categories}
    resolved_ward = ward_map.get(_normalize_dash(ward))
    resolved_category = category_map.get(_normalize_dash(category))
    if resolved_ward is None:
        raise RefusalError(
            f"REFUSAL: ward '{ward}' is not in the dataset. Allowed wards: {wards}"
        )
    if resolved_category is None:
        raise RefusalError(
            f"REFUSAL: category '{category}' is not in the dataset. "
            f"Allowed categories: {categories}"
        )
    ward, category = resolved_ward, resolved_category

    series = [
        r for r in rows if r["ward"] == ward and r["category"] == category
    ]
    series.sort(key=lambda r: r["period"])
    by_period = {r["period"]: r for r in series}

    formula = MOM_FORMULA if growth_type == "MoM" else YOY_FORMULA
    output = []
    for row in series:
        period = row["period"]
        year, month = period.split("-")
        year_n, month_n = int(year), int(month)
        if growth_type == "MoM":
            prior_month = 12 if month_n == 1 else month_n - 1
            prior_year = year_n - 1 if month_n == 1 else year_n
            prior_period = f"{prior_year:04d}-{prior_month:02d}"
        else:
            prior_period = f"{year_n - 1:04d}-{month_n:02d}"

        current = row["actual_spend"]
        prior_row = by_period.get(prior_period)
        prior = prior_row["actual_spend"] if prior_row else None
        notes = row["notes"]

        if current is None:
            output.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": "NULL",
                    "growth_pct": "",
                    "formula": formula,
                    "status": "NULL_FLAGGED",
                    "notes": notes or "actual_spend is null — growth not computed",
                }
            )
            continue

        if prior_row is None:
            output.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": _format_spend(current),
                    "growth_pct": "",
                    "formula": formula,
                    "status": "NO_PRIOR",
                    "notes": f"No {prior_period} row in this ward+category series.",
                }
            )
            continue

        if prior is None:
            output.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": _format_spend(current),
                    "growth_pct": "",
                    "formula": formula,
                    "status": "NOT_COMPUTED",
                    "notes": f"Prior period {prior_period} actual_spend is null — growth not computed.",
                }
            )
            continue

        if prior == 0:
            output.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": _format_spend(current),
                    "growth_pct": "",
                    "formula": formula,
                    "status": "NOT_COMPUTED",
                    "notes": f"Prior period {prior_period} actual_spend is 0 — cannot divide.",
                }
            )
            continue

        growth = (current - prior) / prior * 100
        instantiated = (
            f"{growth_type}: ({current} - {prior}) / {prior} * 100 = {_format_pct(growth)}"
        )
        output.append(
            {
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": _format_spend(current),
                "growth_pct": _format_pct(growth),
                "formula": instantiated,
                "status": "COMPUTED",
                "notes": notes,
            }
        )
    return output


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", default="", help="Exactly one ward name")
    parser.add_argument("--category", default="", help="Exactly one category name")
    parser.add_argument(
        "--growth-type",
        default="",
        dest="growth_type",
        help="MoM or YoY — required, never guessed",
    )
    parser.add_argument("--output", required=True, help="Path to growth_output.csv")
    args = parser.parse_args()

    try:
        if not args.growth_type:
            raise RefusalError(
                "REFUSAL: --growth-type is required. Specify MoM or YoY. "
                "The system will not guess the formula."
            )
        dataset = load_dataset(args.input)
        _print_null_report(dataset)
        table = compute_growth(dataset, args.ward, args.category, args.growth_type)
    except RefusalError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(OUTPUT_FIELDS))
        writer.writeheader()
        writer.writerows(table)
    print(f"Done. Per-ward per-category table written to {args.output}")


if __name__ == "__main__":
    main()
