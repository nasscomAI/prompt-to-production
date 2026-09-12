"""
UC-0C app.py — Growth-analysis agent for "Number That Looks Right".

Computes MoM growth ONLY at the explicitly requested ward + category level
from the supplied budget CSV. Never aggregates across wards or categories.
Flags every NULL actual_spend row before computing and never treats NULL as
zero. Output is a per-period table written to growth_output.csv.

Execution model:
  load_dataset  -> reads + validates the CSV, reports NULL rows
  compute_growth -> filters to the requested ward/category and produces the
                    per-period growth table
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]

SUPPORTED_GROWTH_TYPES = ["MoM"]

OUTPUT_COLUMNS = [
    "period",
    "ward",
    "category",
    "actual_spend",
    "previous_actual_spend",
    "growth_type",
    "formula",
    "growth_percent",
    "status",
    "notes",
]


def _is_null(value):
    """Return True when an actual_spend value is NULL/blank."""
    return value is None or str(value).strip() == ""


def load_dataset(input_path):
    """
    Read and validate the budget CSV.

    Validates that all required columns exist (period, ward, category,
    budgeted_amount, actual_spend, notes). Reports the total row count and
    every NULL actual_spend row with its notes-column reason BEFORE any
    computation. NULL values are preserved as-is and never converted to
    zero.

    Returns: list of dict rows (with NULL actual_spend preserved).
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError("CSV is empty: no header row found")
            missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
            if missing:
                raise ValueError(
                    "Missing required column(s): {}. Required: {}".format(
                        ", ".join(missing), ", ".join(REQUIRED_COLUMNS)
                    )
                )
            rows = [dict(row) for row in reader]
    except FileNotFoundError as e:
        raise FileNotFoundError(
            "Dataset not found at '{}'. Refusing to continue without the "
            "supplied CSV.".format(input_path)
        ) from e
    except csv.Error as e:
        raise ValueError("Failed to parse CSV '{}': {}".format(input_path, e)) from e

    total_rows = len(rows)
    null_rows = [r for r in rows if _is_null(r.get("actual_spend"))]

    print("=== load_dataset: {} ({} rows) ===".format(input_path, total_rows))
    print("Total rows: {}".format(total_rows))
    print("NULL actual_spend rows: {}".format(len(null_rows)))
    for r in null_rows:
        reason = r.get("notes", "").strip() or "(no reason in notes)"
        print(
            "  - {} · {} · {} · actual_spend NULL, reason: {}"
            .format(r["period"], r["ward"], r["category"], reason)
        )

    return rows


def _format_money(value):
    """Return a cleaned string representation for CSV cells."""
    if _is_null(value):
        return ""
    return str(value).strip()


def compute_growth(rows, ward, category, growth_type):
    """
    Produce the per-period MoM growth table for exactly the requested
    ward and category.

    Filters to the exact ward + category (never substitutes or aggregates),
    sorts chronologically by period, and computes MoM per row:
        growth = ((current actual_spend - previous actual_spend)
                  / previous actual_spend) * 100

    NULL handling:
      - If current OR previous actual_spend is NULL, growth is NOT
        calculated; the row is flagged and the NULL reason from the notes
        column is reported. NULL is never treated as zero.
      - The first month has no previous period: growth is marked N/A with an
        explanation.

    Returns: list of output dicts, one per period.
    """
    selected = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not selected:
        raise ValueError(
            "No data found for ward '{}' and category '{}'. Refusing to "
            "write output.".format(ward, category)
        )

    selected = sorted(selected, key=lambda r: r["period"])
    output_rows = []
    previous_value = None

    for r in selected:
        current_value = r.get("actual_spend")
        notes = r.get("notes", "").strip()
        out = {
            "period": r["period"],
            "ward": r["ward"],
            "category": r["category"],
            "actual_spend": _format_money(current_value),
            "previous_actual_spend": "",
            "growth_type": growth_type,
            "formula": "",
            "growth_percent": "",
            "status": "",
            "notes": notes,
        }

        if previous_value is None:
            # First period for this ward+category: no previous month exists.
            out["status"] = "N/A"
            out["formula"] = (
                "No previous month exists for period {} — growth cannot be "
                "calculated against a previous period.".format(r["period"])
            )
            out["previous_actual_spend"] = ""
        elif _is_null(current_value) or _is_null(previous_value):
            # Either side of the comparison is NULL: cannot compute.
            reasons = []
            if _is_null(current_value):
                reasons.append(
                    "current actual_spend is NULL ({})"
                    .format(notes or "no reason in notes")
                )
            if _is_null(previous_value):
                reasons.append(
                    "previous actual_spend is NULL ({})"
                    .format(previous_notes or "no reason in notes")
                )
            out["status"] = "FLAGGED"
            out["previous_actual_spend"] = _format_money(previous_value)
            out["growth_percent"] = ""
            out["formula"] = (
                "Growth not calculated for period {}: {}."
                .format(r["period"], "; ".join(reasons))
            )
        else:
            prev_f = float(previous_value)
            curr_f = float(current_value)
            if prev_f == 0:
                # Avoid division by zero; not a NULL case in this dataset,
                # but refuse to produce a misleading number.
                out["status"] = "FLAGGED"
                out["previous_actual_spend"] = _format_money(previous_value)
                out["formula"] = (
                    "Growth not calculated for period {}: previous "
                    "actual_spend is 0, division by zero.".format(r["period"])
                )
                out["growth_percent"] = ""
            else:
                growth = ((curr_f - prev_f) / prev_f) * 100
                out["status"] = "computed"
                out["previous_actual_spend"] = _format_money(previous_value)
                out["growth_percent"] = "{:.1f}".format(growth)
                out["formula"] = (
                    "(({current} - {previous}) / {previous}) * 100 = "
                    "{growth:.1f}%"
                    .format(
                        current=_format_money(current_value) or "NULL",
                        previous=_format_money(previous_value) or "NULL",
                        growth=growth,
                    )
                )

        output_rows.append(out)
        previous_value = r.get("actual_spend")
        previous_notes = notes

    return output_rows


def write_output(output_rows, output_path):
    """Write the per-period table to the output CSV with proper escaping."""
    if not output_rows:
        raise ValueError("No output rows to write; refusing to write an empty file.")
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(output_rows)


def main():
    parser = argparse.ArgumentParser(
        description="Compute per-period growth for one ward + category."
    )
    parser.add_argument("--input", required=True,
                        help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True,
                        help="Exact ward name to analyze")
    parser.add_argument("--category", required=True,
                        help="Exact category to analyze")
    parser.add_argument("--growth-type", required=True,
                        help="Growth type to compute (supported: MoM)")
    parser.add_argument("--output", required=True,
                        help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Rule: never guess the growth type. Refuse unless explicitly supported.
    if args.growth_type not in SUPPORTED_GROWTH_TYPES:
        print(
            "REFUSE: unsupported growth type '{}'. Supported: {}. "
            "Please specify --growth-type explicitly."
            .format(args.growth_type, ", ".join(SUPPORTED_GROWTH_TYPES)),
            file=sys.stderr,
        )
        sys.exit(1)

    rows = load_dataset(args.input)

    try:
        output_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print("REFUSE: {}".format(e), file=sys.stderr)
        sys.exit(1)

    write_output(output_rows, args.output)
    print("Wrote per-period growth table for '{}' / '{}' ({}) to '{}'."
          .format(args.ward, args.category, args.growth_type, args.output))


if __name__ == "__main__":
    main()