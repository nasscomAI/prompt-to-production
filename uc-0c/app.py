"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv

# Enforcement rule 3 -- see agents.md. A growth cell that cannot be computed
# says so. A blank cell reads as "no change"; a zero reads as "no spend".
MISSING = "MISSING_DATA"

# Not the same thing as MISSING_DATA. The first period has no comparison base by
# definition; that is a property of the series, not a gap in the ledger. Merging
# the two would be the same conflation this UC exists to prevent.
NO_BASE = "NO_PRIOR_PERIOD"


def calculate_growth(input_path, output_path):
    with open(input_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Enforcement rule 2: missing rows are reported before anything is computed.
    missing = [r for r in rows if not r["actual_spend"].strip()]
    print("Missing actual_spend rows: {}".format(len(missing)))
    for row in missing:
        print("  {} | {} | {} | reason: {}".format(
            row["period"], row["ward"], row["category"], row["notes"] or "(none given)"))

    # Enforcement rule 1: an empty cell is absence, not zero. Periods that
    # contain a missing cell are marked, not silently understated.
    totals = {}
    incomplete = set()
    for row in rows:
        period = row["period"]
        if not row["actual_spend"].strip():
            incomplete.add(period)
            continue
        totals[period] = totals.get(period, 0) + float(row["actual_spend"])

    periods = sorted(totals)
    results = []
    previous = None
    previous_ok = False
    for period in periods:
        # Enforcement rule 3: growth against an unknown base is not computable.
        if previous is None:
            growth = NO_BASE
        elif not previous_ok or period in incomplete:
            growth = MISSING
        else:
            growth = round((totals[period] - previous) / previous * 100, 1)
        results.append({
            "period": period,
            "total_spend": round(totals[period], 1),
            "growth_pct": growth,
            "data_complete": "no" if period in incomplete else "yes",
        })
        previous = totals[period]
        previous_ok = period not in incomplete

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["period", "total_spend", "growth_pct", "data_complete"])
        writer.writeheader()
        writer.writerows(results)
        # Enforcement rule 4: incompleteness travels with the results file.
        f.write("# {} rows had missing actual_spend and were excluded\n".format(len(missing)))


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    calculate_growth(args.input, args.output)


if __name__ == "__main__":
    main()
