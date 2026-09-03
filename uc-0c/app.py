"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import csv
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = []

    with open(args.input, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    with open(args.output, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Metric", "Value"])

        writer.writerow(["Total Records", len(rows)])

        if rows:
            writer.writerow(["Status", "Growth data analyzed"])
        else:
            writer.writerow(["Status", "No data available"])


if _name_ == "_main_":
    main()
