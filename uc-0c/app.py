"""
UC-0C — Ward Budget Growth Calculator
Implements load_dataset and compute_growth per agents.md + skills.md.
"""
import argparse
import csv
import os

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]
OUTPUT_COLUMNS = [
    "period",
    "ward",
    "category",
    "actual_spend",
    "growth_pct",
    "formula",
    "null_flag",
    "null_reason",
]
AGGREGATION_MARKERS = {"all", "*", "any", "every"}


def _parse_actual_spend(value: str | None) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    return float(value)


def load_dataset(path: str) -> dict:
    resolved = os.path.abspath(path)
    if not os.path.exists(resolved):
        raise FileNotFoundError(f"Input file not found: {resolved}")

    try:
        with open(resolved, newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            if not fieldnames:
                raise ValueError(f"File is not valid CSV: {resolved}")

            for column in REQUIRED_COLUMNS:
                if column not in fieldnames:
                    raise ValueError(
                        f"Required column '{column}' is absent from the CSV header"
                    )

            raw_rows = list(reader)
    except csv.Error as exc:
        raise ValueError(f"File is not valid CSV: {resolved}") from exc

    if not raw_rows:
        raise ValueError("Dataset is empty")

    rows = []
    null_report = []

    for raw in raw_rows:
        actual_spend = _parse_actual_spend(raw.get("actual_spend"))
        row = {
            "period": raw["period"].strip(),
            "ward": raw["ward"].strip(),
            "category": raw["category"].strip(),
            "budgeted_amount": float(raw["budgeted_amount"]),
            "actual_spend": actual_spend,
            "notes": (raw.get("notes") or "").strip(),
        }
        rows.append(row)
        if actual_spend is None:
            null_report.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "notes": row["notes"],
                }
            )

    return {
        "rows": rows,
        "null_report": null_report,
        "null_count": len(null_report),
    }


def _format_growth_pct(value: float) -> str:
    if value >= 0:
        return f"+{value:.1f}%"
    return f"−{abs(value):.1f}%"


def _previous_period_mom(period: str) -> str:
    year, month = period.split("-")
    year_int, month_int = int(year), int(month)
    if month_int == 1:
        return f"{year_int - 1}-12"
    return f"{year}-{month_int - 1:02d}"


def _previous_period_yoy(period: str) -> str:
    year, month = period.split("-")
    return f"{int(year) - 1}-{month}"


def _refuse_aggregation(ward: str, category: str) -> None:
    if not ward or not category:
        raise ValueError(
            "Per-ward per-category granularity is required. "
            "Specify both --ward and --category."
        )
    if ward.lower() in AGGREGATION_MARKERS or category.lower() in AGGREGATION_MARKERS:
        raise ValueError(
            "Per-ward per-category granularity is required — "
            "aggregation across all wards or categories is not permitted."
        )


def compute_growth(
    dataset: dict,
    ward: str,
    category: str,
    growth_type: str,
    output_path: str,
) -> None:
    if growth_type is None or not str(growth_type).strip():
        raise ValueError("--growth-type is required. Specify MoM or YoY.")

    growth_type = growth_type.strip()
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            f"Unsupported growth-type: {growth_type}. Use MoM or YoY."
        )

    rows = dataset.get("rows")
    if not rows:
        raise ValueError("No dataset rows were provided")

    ward = ward.strip()
    category = category.strip()
    _refuse_aggregation(ward, category)

    all_wards = {row["ward"] for row in rows}
    if ward not in all_wards:
        raise ValueError(f"Invalid ward: {ward}")

    ward_categories = {row["category"] for row in rows if row["ward"] == ward}
    if category not in ward_categories:
        raise ValueError(f"Invalid category for ward '{ward}': {category}")

    filtered = [
        row for row in rows if row["ward"] == ward and row["category"] == category
    ]
    filtered.sort(key=lambda row: row["period"])
    rows_by_period = {row["period"]: row for row in filtered}

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if not os.path.isdir(out_dir) or not os.access(out_dir, os.W_OK):
        raise IOError(
            f"Output directory does not exist or is not writable: {out_dir}"
        )

    output_rows = []
    for row in filtered:
        period = row["period"]
        actual_spend = row["actual_spend"]
        output_row = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": "" if actual_spend is None else actual_spend,
            "growth_pct": "",
            "formula": "",
            "null_flag": "",
            "null_reason": "",
        }

        if actual_spend is None:
            output_row["null_flag"] = "TRUE"
            output_row["null_reason"] = row["notes"]
            output_rows.append(output_row)
            continue

        if growth_type == "MoM":
            comparison_period = _previous_period_mom(period)
            formula_label = "MoM: ((current − previous) / previous) × 100"
        else:
            comparison_period = _previous_period_yoy(period)
            formula_label = "YoY: ((current − prior_year) / prior_year) × 100"

        comparison_row = rows_by_period.get(comparison_period)
        comparison_spend = (
            comparison_row["actual_spend"] if comparison_row is not None else None
        )

        if comparison_row is None or comparison_spend is None:
            output_row["growth_pct"] = "NOT_COMPUTED"
            if comparison_row is None:
                output_row["formula"] = (
                    f"{formula_label} — comparison period "
                    f"{comparison_period} not in dataset"
                )
            else:
                output_row["formula"] = (
                    f"{formula_label} — comparison period "
                    f"{comparison_period} has null actual_spend"
                )
            output_rows.append(output_row)
            continue

        growth = ((actual_spend - comparison_spend) / comparison_spend) * 100
        growth_str = _format_growth_pct(growth)
        output_row["growth_pct"] = growth_str
        if growth_type == "MoM":
            output_row["formula"] = (
                f"MoM: (({actual_spend} − {comparison_spend}) / "
                f"{comparison_spend}) × 100 = {growth_str}"
            )
        else:
            output_row["formula"] = (
                f"YoY: (({actual_spend} − {comparison_spend}) / "
                f"{comparison_spend}) × 100 = {growth_str}"
            )
        output_rows.append(output_row)

    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(output_rows)


def _print_null_report(null_report: list[dict]) -> None:
    print(f"Null report: {len(null_report)} row(s) with missing actual_spend:")
    for entry in null_report:
        reason = entry["notes"] or "(no reason provided)"
        print(
            f"  {entry['period']} · {entry['ward']} · "
            f"{entry['category']} — {reason}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="UC-0C Ward Budget Growth Calculator"
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (exact match)")
    parser.add_argument(
        "--category", required=True, help="Category name (exact match)"
    )
    parser.add_argument(
        "--growth-type",
        required=True,
        dest="growth_type",
        help="MoM or YoY",
    )
    parser.add_argument(
        "--output", required=True, help="Path to write growth_output.csv"
    )
    args = parser.parse_args()

    dataset = load_dataset(args.input)
    if dataset["null_count"] > 0:
        _print_null_report(dataset["null_report"])

    compute_growth(
        dataset,
        args.ward,
        args.category,
        args.growth_type,
        args.output,
    )
    print(f"Done. Growth table written to {args.output}")


if __name__ == "__main__":
    main()
