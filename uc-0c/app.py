"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def load_dataset(input_path: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    with open(input_path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Input CSV does not contain a header row.")

        missing = REQUIRED_COLUMNS.difference(reader.fieldnames)
        if missing:
            raise ValueError(f"Input CSV missing required columns: {sorted(missing)}")

        rows = list(reader)

    null_rows: list[dict[str, str]] = []
    for row in rows:
        if not str(row.get("actual_spend", "")).strip():
            null_rows.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "notes": row.get("notes", "").strip(),
                }
            )

    return rows, null_rows


def _parse_float(value: str) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return float(text)


def compute_growth(
    rows: list[dict[str, str]],
    ward: str,
    category: str,
    growth_type: str,
) -> list[dict[str, str]]:
    if not growth_type:
        raise ValueError("--growth-type is required. Use MoM or YoY.")

    normalized_growth_type = growth_type.strip().upper()
    if normalized_growth_type not in {"MOM", "YOY"}:
        raise ValueError("Unsupported growth type. Use MoM or YoY.")

    if not ward.strip() or not category.strip():
        raise ValueError("Ward and category are required; aggregate requests are refused.")

    ward_values = {row["ward"] for row in rows}
    category_values = {row["category"] for row in rows}
    if ward not in ward_values:
        raise ValueError(f"Unknown ward: {ward}")
    if category not in category_values:
        raise ValueError(f"Unknown category: {category}")

    filtered = [
        row for row in rows if row["ward"] == ward and row["category"] == category
    ]
    filtered.sort(key=lambda row: row["period"])

    results: list[dict[str, str]] = []
    for index, row in enumerate(filtered):
        current_value = _parse_float(row["actual_spend"])
        if normalized_growth_type == "MOM":
            previous_row = filtered[index - 1] if index > 0 else None
        else:
            previous_row = None
            for candidate in filtered:
                if candidate["period"] == f"{int(row['period'][:4]) - 1}-{row['period'][5:]}":
                    previous_row = candidate
                    break

        previous_value = _parse_float(previous_row["actual_spend"]) if previous_row else None

        formula = ""
        growth = ""
        status = "OK"
        note = ""

        if current_value is None:
            status = "FLAG_NULL"
            note = row.get("notes", "").strip() or "Null actual_spend"
            formula = "Cannot compute growth: current actual_spend is NULL"
        elif previous_row is None:
            status = "NO_BASELINE"
            formula = "Cannot compute growth: no prior period available"
        elif previous_value is None:
            status = "FLAG_NULL"
            note = previous_row.get("notes", "").strip() or "Prior period actual_spend is NULL"
            formula = "Cannot compute growth: prior period actual_spend is NULL"
        elif previous_value == 0:
            status = "NO_BASELINE"
            formula = "Cannot compute growth: prior period actual_spend is 0"
        else:
            growth_value = ((current_value - previous_value) / previous_value) * 100
            growth = f"{growth_value:+.1f}%"
            formula = (
                f"(({current_value:.1f} - {previous_value:.1f}) / {previous_value:.1f}) * 100"
            )

        results.append(
            {
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": "" if current_value is None else f"{current_value:.1f}",
                "growth_type": normalized_growth_type,
                "growth": growth,
                "formula": formula,
                "status": status,
                "notes": note,
            }
        )

    return results


def write_output(output_path: str, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "growth",
        "formula",
        "status",
        "notes",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    dataset, null_rows = load_dataset(args.input)
    if null_rows:
        print("Null actual_spend rows detected before computation:")
        for row in null_rows:
            print(
                f"- {row['period']} | {row['ward']} | {row['category']} | note: {row['notes']}"
            )

    output_rows = compute_growth(dataset, args.ward, args.category, args.growth_type)
    write_output(args.output, output_rows)
    print(f"Done. Growth output written to {args.output}")

if __name__ == "__main__":
    main()
