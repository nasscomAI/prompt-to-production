"""UC-0C app: ward-category growth computation with null-safe rules."""
import argparse
import csv
import re

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(input_path: str) -> tuple[list[dict], list[dict]]:
    with open(input_path, "r", newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader.fieldnames:
            raise ValueError("Input CSV has no header.")
        missing = REQUIRED_COLUMNS.difference(set(reader.fieldnames))
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        rows = list(reader)

    null_rows = [
        {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "notes": (row.get("notes") or "").strip(),
        }
        for row in rows
        if (row.get("actual_spend") or "").strip() == ""
    ]
    return rows, null_rows


def _parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    return float(value)


def _period_minus_12(period: str) -> str:
    year_str, month_str = period.split("-")
    year = int(year_str) - 1
    return f"{year:04d}-{month_str}"


def _normalize_key(value: str) -> str:
    lowered = (value or "").strip().lower()
    return re.sub(r"[^a-z0-9]+", "", lowered)


def compute_growth(rows: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    if not growth_type:
        raise ValueError("Refusal: --growth-type is required. Please specify MoM or YoY.")

    growth_type = growth_type.strip()
    if growth_type not in {"MoM", "YoY"}:
        raise ValueError("Refusal: --growth-type must be exactly MoM or YoY.")

    if ward.strip().lower() in {"all", "all wards", "*", ""} or category.strip().lower() in {"all", "all categories", "*", ""}:
        raise ValueError("Refusal: aggregation across wards/categories is not allowed for UC-0C.")

    ward_key = _normalize_key(ward)
    category_key = _normalize_key(category)

    filtered = [
        row
        for row in rows
        if _normalize_key(row["ward"]) == ward_key and _normalize_key(row["category"]) == category_key
    ]
    if not filtered:
        raise ValueError("No rows found for the specified ward/category.")

    canonical_ward = filtered[0]["ward"]
    canonical_category = filtered[0]["category"]

    filtered.sort(key=lambda item: item["period"])
    by_period = {row["period"]: row for row in filtered}

    output = []
    prev_actual = None
    for row in filtered:
        period = row["period"]
        actual = _parse_float(row.get("actual_spend"))
        notes = (row.get("notes") or "").strip()

        out = {
            "period": period,
            "ward": canonical_ward,
            "category": canonical_category,
            "actual_spend": "" if actual is None else f"{actual:.1f}",
            "prior_period_value": "",
            "growth_type": growth_type,
            "formula": "",
            "growth_percent": "",
            "status": "",
            "notes": notes,
        }

        if actual is None:
            out["status"] = "FLAG_NULL"
            out["notes"] = notes or "actual_spend is null"
            output.append(out)
            if growth_type == "MoM":
                prev_actual = None
            continue

        if growth_type == "MoM":
            if prev_actual is None or prev_actual == 0:
                out["status"] = "BASELINE_OR_PREV_NULL"
                out["notes"] = notes or "No valid previous month actual_spend"
            else:
                growth = ((actual - prev_actual) / prev_actual) * 100
                out["prior_period_value"] = f"{prev_actual:.1f}"
                out["formula"] = "((current_actual - previous_actual) / previous_actual) * 100"
                out["growth_percent"] = f"{growth:+.1f}%"
                out["status"] = "COMPUTED"
            prev_actual = actual
        else:
            prior_period = _period_minus_12(period)
            prior_row = by_period.get(prior_period)
            prior_actual = _parse_float(prior_row.get("actual_spend")) if prior_row else None
            if prior_actual is None or prior_actual == 0:
                out["status"] = "NO_PRIOR_YEAR_DATA"
                out["notes"] = notes or "No valid prior-year value for YoY"
            else:
                growth = ((actual - prior_actual) / prior_actual) * 100
                out["prior_period_value"] = f"{prior_actual:.1f}"
                out["formula"] = "((current_actual - prior_year_actual) / prior_year_actual) * 100"
                out["growth_percent"] = f"{growth:+.1f}%"
                out["status"] = "COMPUTED"

        output.append(out)

    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    result_rows = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "actual_spend", "prior_period_value", "growth_type", "formula", "growth_percent", "status", "notes"]
    with open(args.output, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result_rows)

    print(f"Null rows detected in dataset: {len(null_rows)}")
    for null_row in null_rows:
        reason = null_row["notes"] if null_row["notes"] else "not provided"
        print(f"NULL -> {null_row['period']} | {null_row['ward']} | {null_row['category']} | reason: {reason}")

    print(f"Done. Growth output written to {args.output}")


if __name__ == "__main__":
    main()
