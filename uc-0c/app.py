"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}

EXPECTED_NULL_ROWS = {
    ("2024-03", "Ward 2 – Shivajinagar", "Drainage & Flooding"): "Data not submitted by ward office",
    ("2024-07", "Ward 4 – Warje", "Roads & Pothole Repair"): "Audit freeze — figures under review",
    ("2024-11", "Ward 1 – Kasba", "Waste Management"): None,
    ("2024-08", "Ward 3 – Kothrud", "Parks & Greening"): None,
    ("2024-05", "Ward 5 – Hadapsar", "Streetlight Maintenance"): None,
}


@dataclass(frozen=True)
class BudgetRow:
    period: str
    ward: str
    category: str
    budgeted_amount: float
    actual_spend: float | None
    notes: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute ward-category growth from the municipal budget dataset.")
    parser.add_argument("--input", required=True, help="Path to the ward budget CSV file.")
    parser.add_argument("--ward", required=True, help="Exact ward name to analyze.")
    parser.add_argument("--category", required=True, help="Exact category name to analyze.")
    parser.add_argument("--growth-type", dest="growth_type", required=True, help="Growth type to compute, for example MoM.")
    parser.add_argument("--output", required=True, help="Path to write the growth output CSV.")
    return parser.parse_args()


def resolve_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return (Path(__file__).resolve().parent / path).resolve()


def validate_selection(value: str, field_name: str) -> None:
    lowered = value.strip().lower()
    if lowered in {"", "all", "any", "*"}:
        raise ValueError(f"Refusing {field_name}={value!r}: all-ward or cross-category aggregation is not allowed.")


def parse_float(value: str, field_name: str) -> float:
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"Invalid {field_name} value: {value!r}") from exc


def load_dataset(input_path: Path) -> tuple[list[BudgetRow], list[BudgetRow]]:
    if input_path.suffix.lower() != ".csv":
        raise ValueError(f"Expected a .csv file, got: {input_path}")
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV file is missing a header row.")

        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing_columns:
            missing_text = ", ".join(sorted(missing_columns))
            raise ValueError(f"CSV file is missing required columns: {missing_text}")

        rows: list[BudgetRow] = []
        null_rows: list[BudgetRow] = []
        for raw_row in reader:
            actual_spend_text = (raw_row["actual_spend"] or "").strip()
            row = BudgetRow(
                period=raw_row["period"].strip(),
                ward=raw_row["ward"].strip(),
                category=raw_row["category"].strip(),
                budgeted_amount=parse_float(raw_row["budgeted_amount"].strip(), "budgeted_amount"),
                actual_spend=None if actual_spend_text == "" else parse_float(actual_spend_text, "actual_spend"),
                notes=(raw_row["notes"] or "").strip(),
            )
            rows.append(row)
            if row.actual_spend is None:
                null_rows.append(row)

    validate_null_rows(null_rows)
    return rows, null_rows


def validate_null_rows(null_rows: list[BudgetRow]) -> None:
    actual_null_map = {(row.period, row.ward, row.category): row.notes or None for row in null_rows}
    if len(null_rows) != 5:
        raise ValueError(f"Expected 5 null actual_spend rows, found {len(null_rows)}")
    if set(actual_null_map) != set(EXPECTED_NULL_ROWS):
        missing = sorted(set(EXPECTED_NULL_ROWS) - set(actual_null_map))
        unexpected = sorted(set(actual_null_map) - set(EXPECTED_NULL_ROWS))
        message_parts = []
        if missing:
            message_parts.append(f"missing expected null rows: {missing}")
        if unexpected:
            message_parts.append(f"unexpected null rows: {unexpected}")
        raise ValueError("Null-row validation failed: " + "; ".join(message_parts))

    for key, expected_note in EXPECTED_NULL_ROWS.items():
        actual_note = actual_null_map[key]
        if expected_note is not None and actual_note != expected_note:
            raise ValueError(f"Null-row note mismatch for {key}: expected {expected_note!r}, got {actual_note!r}")


def filter_rows(rows: list[BudgetRow], ward: str, category: str) -> list[BudgetRow]:
    selected = [row for row in rows if row.ward == ward and row.category == category]
    if not selected:
        raise ValueError(f"No rows found for ward={ward!r} and category={category!r}")
    return sorted(selected, key=lambda row: row.period)


def format_decimal(value: float) -> str:
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.1f}%"


def compute_mom_output(rows: list[BudgetRow]) -> list[dict[str, str]]:
    output_rows: list[dict[str, str]] = []
    previous_row: BudgetRow | None = None

    for row in rows:
        base = {
            "period": row.period,
            "ward": row.ward,
            "category": row.category,
            "actual_spend": "NULL" if row.actual_spend is None else format_decimal(row.actual_spend),
            "growth_type": "MoM",
            "growth_percent": "",
            "formula": "",
            "status": "",
            "notes": row.notes,
        }

        if row.actual_spend is None:
            base["status"] = "FLAGGED_NULL"
            base["formula"] = "Not computed because actual_spend is NULL"
            output_rows.append(base)
            previous_row = row
            continue

        if previous_row is None:
            base["status"] = "NO_PRIOR_PERIOD"
            base["formula"] = "MoM requires previous period actual_spend"
            output_rows.append(base)
            previous_row = row
            continue

        if previous_row.actual_spend is None:
            base["status"] = "PREVIOUS_PERIOD_NULL"
            base["formula"] = "Not computed because previous period actual_spend is NULL"
            output_rows.append(base)
            previous_row = row
            continue

        if previous_row.actual_spend == 0:
            base["status"] = "PREVIOUS_PERIOD_ZERO"
            base["formula"] = "Not computed because previous period actual_spend is 0"
            output_rows.append(base)
            previous_row = row
            continue

        growth_value = ((row.actual_spend - previous_row.actual_spend) / previous_row.actual_spend) * 100
        base["growth_percent"] = format_percent(growth_value)
        base["formula"] = (
            f"(({format_decimal(row.actual_spend)} - {format_decimal(previous_row.actual_spend)}) / "
            f"{format_decimal(previous_row.actual_spend)}) * 100 = {format_percent(growth_value)}"
        )
        base["status"] = "COMPUTED"
        output_rows.append(base)
        previous_row = row

    return output_rows


def compute_growth(rows: list[BudgetRow], ward: str, category: str, growth_type: str) -> list[dict[str, str]]:
    validate_selection(ward, "ward")
    validate_selection(category, "category")
    if not growth_type.strip():
        raise ValueError("growth_type is required; refuse to guess between MoM and YoY.")

    normalized_growth = growth_type.strip().upper()
    if normalized_growth != "MOM":
        raise ValueError(f"Unsupported growth_type {growth_type!r}. This UC expects an explicit supported value such as MoM.")

    selected_rows = filter_rows(rows, ward, category)
    return compute_mom_output(selected_rows)


def lookup_row(rows: list[BudgetRow], period: str, ward: str, category: str) -> BudgetRow:
    for row in rows:
        if row.period == period and row.ward == ward and row.category == category:
            return row
    raise ValueError(f"Reference row not found for {(period, ward, category)}")


def verify_reference_values(rows: list[BudgetRow]) -> None:
    july = lookup_row(rows, "2024-07", "Ward 1 – Kasba", "Roads & Pothole Repair")
    june = lookup_row(rows, "2024-06", "Ward 1 – Kasba", "Roads & Pothole Repair")
    october = lookup_row(rows, "2024-10", "Ward 1 – Kasba", "Roads & Pothole Repair")
    september = lookup_row(rows, "2024-09", "Ward 1 – Kasba", "Roads & Pothole Repair")
    shivajinagar_null = lookup_row(rows, "2024-03", "Ward 2 – Shivajinagar", "Drainage & Flooding")
    warje_null = lookup_row(rows, "2024-07", "Ward 4 – Warje", "Roads & Pothole Repair")

    if july.actual_spend != 19.7:
        raise ValueError(f"README check failed for 2024-07 Kasba Roads actual_spend: expected 19.7, got {july.actual_spend}")
    july_growth = round(((july.actual_spend - june.actual_spend) / june.actual_spend) * 100, 1)
    if july_growth != 33.1:
        raise ValueError(f"README check failed for 2024-07 Kasba Roads MoM: expected 33.1, got {july_growth}")

    if october.actual_spend != 13.1:
        raise ValueError(f"README check failed for 2024-10 Kasba Roads actual_spend: expected 13.1, got {october.actual_spend}")
    october_growth = round(((october.actual_spend - september.actual_spend) / september.actual_spend) * 100, 1)
    if october_growth != -34.8:
        raise ValueError(f"README check failed for 2024-10 Kasba Roads MoM: expected -34.8, got {october_growth}")

    if shivajinagar_null.actual_spend is not None:
        raise ValueError("README check failed: 2024-03 Ward 2 – Shivajinagar Drainage & Flooding must be NULL")
    if warje_null.actual_spend is not None:
        raise ValueError("README check failed: 2024-07 Ward 4 – Warje Roads & Pothole Repair must be NULL")


def write_output(output_path: Path, output_rows: list[dict[str, str]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "growth_percent",
        "formula",
        "status",
        "notes",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)


def main() -> None:
    args = parse_args()
    input_path = resolve_path(args.input)
    output_path = resolve_path(args.output)

    rows, _null_rows = load_dataset(input_path)
    verify_reference_values(rows)
    output_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_output(output_path, output_rows)


if __name__ == "__main__":
    main()
