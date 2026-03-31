"""UC-0C budget growth analyzer.

Computes per-period growth for exactly one ward and one category.
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]
SUPPORTED_GROWTH_TYPES = {"MOM", "YOY"}


@dataclass(frozen=True)
class ValidationReport:
    row_count: int
    distinct_wards: int
    distinct_categories: int
    null_rows: List[Dict[str, str]]


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute ward-category growth table.")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--ward", required=True, help="Exact ward value")
    parser.add_argument("--category", required=True, help="Exact category value")
    parser.add_argument(
        "--growth-type",
        dest="growth_type",
        help="Growth type: MoM or YoY",
    )
    parser.add_argument("--output", required=True, help="Output CSV path")
    return parser.parse_args(argv)


def normalize_growth_type(value: Optional[str]) -> str:
    if not value:
        raise ValueError("Missing --growth-type. Specify one of: MoM, YoY.")

    normalized = value.strip().upper()
    if normalized not in SUPPORTED_GROWTH_TYPES:
        raise ValueError(
            "Unsupported growth type. Specify exactly one of: MoM, YoY."
        )
    return normalized


def looks_like_aggregation_request(value: str) -> bool:
    candidate = value.strip().lower()
    blocked_tokens = {"any", "all", "*", "overall", "citywide", "city-wide"}
    if candidate in blocked_tokens:
        return True
    if "," in candidate or " and " in candidate or "/" in candidate:
        return True
    return False


def parse_float_or_none(value: str) -> Optional[float]:
    if value is None:
        return None
    stripped = value.strip()
    if stripped == "":
        return None
    try:
        return float(stripped)
    except ValueError as exc:
        raise ValueError(f"Invalid numeric value for actual_spend: {value!r}") from exc


def load_dataset(input_path: Path) -> Tuple[List[Dict[str, str]], ValidationReport]:
    if not input_path.exists() or not input_path.is_file():
        raise ValueError(f"Input CSV not found: {input_path}")

    try:
        with input_path.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            missing = [col for col in REQUIRED_COLUMNS if col not in fieldnames]
            if missing:
                raise ValueError(
                    "Input CSV is missing required columns: " + ", ".join(missing)
                )

            rows = [dict(row) for row in reader]
    except OSError as exc:
        raise ValueError(f"Unable to read input CSV: {input_path}") from exc

    null_rows: List[Dict[str, str]] = []
    wards = set()
    categories = set()

    for row in rows:
        wards.add((row.get("ward") or "").strip())
        categories.add((row.get("category") or "").strip())
        if parse_float_or_none(row.get("actual_spend", "")) is None:
            null_rows.append(
                {
                    "period": (row.get("period") or "").strip(),
                    "ward": (row.get("ward") or "").strip(),
                    "category": (row.get("category") or "").strip(),
                    "notes": (row.get("notes") or "").strip(),
                }
            )

    report = ValidationReport(
        row_count=len(rows),
        distinct_wards=len({w for w in wards if w}),
        distinct_categories=len({c for c in categories if c}),
        null_rows=null_rows,
    )
    return rows, report


def resolve_exact_value(
    values: Sequence[str], requested: str, label: str
) -> str:
    def canonical(text: str) -> str:
        normalized = text.strip().lower()
        normalized = (
            normalized.replace("–", "-")
            .replace("—", "-")
            .replace("−", "-")
        )
        normalized = " ".join(normalized.split())
        return normalized

    requested_clean = requested.strip()
    if not requested_clean:
        raise ValueError(f"Missing {label}. Provide exactly one {label}.")

    if looks_like_aggregation_request(requested_clean):
        raise ValueError(
            f"Refused: {label} must be exactly one value. Aggregated requests are not allowed."
        )

    requested_key = canonical(requested_clean)
    matches = [value for value in values if canonical(value) == requested_key]
    unique_matches = sorted(set(matches))
    if len(unique_matches) == 0:
        raise ValueError(f"Unknown {label}: {requested}.")
    if len(unique_matches) > 1:
        raise ValueError(f"Ambiguous {label}: {requested}. Provide exact spelling.")
    return unique_matches[0]


def compute_growth_rows(
    rows: Sequence[Dict[str, str]],
    ward: str,
    category: str,
    growth_type: str,
) -> List[Dict[str, str]]:
    filtered = [
        row
        for row in rows
        if (row.get("ward") or "").strip() == ward
        and (row.get("category") or "").strip() == category
    ]
    if not filtered:
        raise ValueError(
            "No rows found for the selected ward and category in the provided dataset."
        )

    filtered.sort(key=lambda row: (row.get("period") or "").strip())
    period_to_row = {(row.get("period") or "").strip(): row for row in filtered}
    output_rows: List[Dict[str, str]] = []

    for row in filtered:
        period = (row.get("period") or "").strip()
        actual_value = parse_float_or_none(row.get("actual_spend", ""))
        notes = (row.get("notes") or "").strip()

        out: Dict[str, str] = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": "" if actual_value is None else f"{actual_value:.6g}",
            "growth_value": "",
            "growth_type": growth_type,
            "formula_used": "",
            "status": "",
            "null_reason": "",
        }

        if actual_value is None:
            out["status"] = "null_flagged_with_reason"
            out["null_reason"] = notes
            output_rows.append(out)
            continue

        previous_row = None
        if growth_type == "MOM":
            year, month = period.split("-", 1)
            prev_year = int(year)
            prev_month = int(month) - 1
            if prev_month == 0:
                prev_year -= 1
                prev_month = 12
            prev_period = f"{prev_year:04d}-{prev_month:02d}"
            previous_row = period_to_row.get(prev_period)
            out["formula_used"] = "MoM = (current - previous) / previous * 100"
        elif growth_type == "YOY":
            year, month = period.split("-", 1)
            prev_period = f"{int(year) - 1:04d}-{int(month):02d}"
            previous_row = period_to_row.get(prev_period)
            out["formula_used"] = "YoY = (current - same_period_last_year) / same_period_last_year * 100"

        if previous_row is None:
            out["status"] = "not_computed_missing_previous_period"
            output_rows.append(out)
            continue

        prev_actual = parse_float_or_none(previous_row.get("actual_spend", ""))
        if prev_actual is None:
            out["status"] = "not_computed_previous_period_null"
            output_rows.append(out)
            continue

        if prev_actual == 0:
            out["status"] = "not_computed_previous_period_zero"
            output_rows.append(out)
            continue

        growth = ((actual_value - prev_actual) / prev_actual) * 100.0
        out["growth_value"] = f"{growth:.6g}"
        out["status"] = "computed"
        output_rows.append(out)

    return output_rows


def write_output(output_path: Path, rows: Sequence[Dict[str, str]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_value",
        "growth_type",
        "formula_used",
        "status",
        "null_reason",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_validation_report(report: ValidationReport) -> None:
    print(
        "Validation report: "
        f"rows={report.row_count}, "
        f"distinct_wards={report.distinct_wards}, "
        f"distinct_categories={report.distinct_categories}, "
        f"null_actual_spend_rows={len(report.null_rows)}"
    )
    if report.null_rows:
        print("Null actual_spend rows (flagged before compute):")
        for row in report.null_rows:
            print(
                "- "
                f"period={row['period']}, ward={row['ward']}, "
                f"category={row['category']}, notes={row['notes']}"
            )


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    try:
        growth_type = normalize_growth_type(args.growth_type)
        rows, report = load_dataset(Path(args.input))
        print_validation_report(report)

        wards = sorted({(row.get("ward") or "").strip() for row in rows if row.get("ward")})
        categories = sorted(
            {(row.get("category") or "").strip() for row in rows if row.get("category")}
        )
        ward = resolve_exact_value(wards, args.ward, "ward")
        category = resolve_exact_value(categories, args.category, "category")

        growth_rows = compute_growth_rows(rows, ward, category, growth_type)
        write_output(Path(args.output), growth_rows)
        print(f"Wrote {len(growth_rows)} rows to {args.output}")
        return 0
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
