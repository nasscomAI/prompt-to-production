"""
UC-0C — Number That Looks Right
Ward-level growth calculator built to the agents.md enforcement rules:
single ward × single category only, nulls flagged with their notes-column
reason before any computation, the formula shown on every computed row,
and explicit refusals instead of silent guesses.
"""
import argparse
import csv


class Refusal(SystemExit):
    def __init__(self, message):
        super().__init__("REFUSAL: " + message)


REQUIRED_COLUMNS = ["period", "ward", "category",
                    "budgeted_amount", "actual_spend", "notes"]


def _read_csv(input_path):
    try:
        f = open(input_path, newline="", encoding="utf-8-sig")
        data = f.read()
    except UnicodeDecodeError:
        f = open(input_path, newline="", encoding="cp1252")
        data = f.read()
    finally:
        f.close()
    return data.splitlines()


def load_dataset(input_path):
    """Read CSV, validate columns, report null count and which rows."""
    lines = _read_csv(input_path)
    reader = csv.DictReader(lines)
    missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
    if missing:
        raise Refusal("input is missing required columns: %s"
                      % ", ".join(missing))

    rows = []
    for row in reader:
        raw_spend = (row.get("actual_spend") or "").strip()
        raw_budget = (row.get("budgeted_amount") or "").strip()
        rows.append({
            "period": row["period"].strip(),
            "ward": row["ward"].strip(),
            "category": row["category"].strip(),
            "budgeted_amount": float(raw_budget) if raw_budget else None,
            "actual_spend": float(raw_spend) if raw_spend else None,
            "notes": (row.get("notes") or "").strip(),
        })

    null_rows = [{"period": r["period"], "ward": r["ward"],
                  "category": r["category"],
                  "notes": r["notes"] or "(no notes)"}
                 for r in rows if r["actual_spend"] is None]
    print("Loaded %d rows. Null actual_spend rows: %d" %
          (len(rows), len(null_rows)))
    for n in null_rows:
        print("  - %(period)s | %(ward)s | %(category)s | reason: %(notes)s" % n)
    return rows


def _fmt(value):
    return "%.1f" % value


def compute_growth(rows, ward, category, growth_type):
    """Return per-period table for one ward x one category, formula shown."""
    if growth_type is None:
        raise Refusal("--growth-type was not specified. Which growth type "
                      "should be used? Supported: MoM. Refusing to guess.")

    gt = growth_type.strip().upper()
    if gt == "YOY":
        years = sorted({r["period"][:4] for r in rows})
        raise Refusal("YoY growth needs a prior-year baseline but the dataset "
                      "only covers %s. Provide earlier data or use MoM."
                      % ", ".join(years))
    if gt != "MOM":
        raise Refusal("unsupported --growth-type '%s'. Supported: MoM."
                      % growth_type)

    series = sorted((r for r in rows
                     if r["ward"] == ward and r["category"] == category),
                    key=lambda r: r["period"])
    if not series:
        wards = "\n".join("  - " + w for w in sorted({r["ward"] for r in rows}))
        cats = "\n".join("  - " + c for c in sorted({r["category"] for r in rows}))
        raise Refusal("no rows for ward=%r category=%r.\nValid wards:\n%s\n"
                      "Valid categories:\n%s" % (ward, category, wards, cats))

    table, prev = [], None
    for row in series:
        cur = row["actual_spend"]
        entry = {"period": row["period"],
                 "budgeted_amount": (_fmt(row["budgeted_amount"])
                                     if row["budgeted_amount"] is not None else ""),
                 "actual_spend": _fmt(cur) if cur is not None else "NULL",
                 "growth_pct": "", "formula": "", "flag": ""}
        if cur is None:
            entry["flag"] = "NULL - not computed (%s)" % (
                row["notes"] or "reason not given")
            entry["growth_pct"] = "N/A"
        elif prev is None:
            entry["growth_pct"] = "n/a"
            entry["formula"] = "-"
            entry["flag"] = "baseline period"
        elif prev["actual_spend"] is None:
            entry["growth_pct"] = "N/A"
            entry["formula"] = "-"
            entry["flag"] = ("N/A - prior period %s actual_spend is NULL"
                             % prev["period"])
        else:
            base = prev["actual_spend"]
            pct = (cur - base) / base * 100.0
            entry["growth_pct"] = "%+.1f%%" % pct
            entry["formula"] = "(%s - %s) / %s * 100 = %+.1f%%" % (
                _fmt(cur), _fmt(base), _fmt(base), pct)
        table.append(entry)
        prev = row
    return table


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyst")
    parser.add_argument("--input", required=True,
                        help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True,
                        help="Exact ward name (single ward only)")
    parser.add_argument("--category", required=True,
                        help="Exact category name (single category only)")
    parser.add_argument("--growth-type", default=None,
                        help="Growth type: MoM (YoY unsupported for 2024-only data)")
    parser.add_argument("--output", required=True,
                        help="Path to write growth_output.csv")
    args = parser.parse_args()

    rows = load_dataset(args.input)
    table = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "budgeted_amount", "actual_spend",
                  "growth_pct", "formula", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(table)
    print("Done. %d periods written to %s" % (len(table), args.output))


if __name__ == "__main__":
    main()
