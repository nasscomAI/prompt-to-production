"""
UC-0B app.py — Starter file.
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

    total_leave = 0
    employee_count = 0

    with open(args.input, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            employee_count += 1

            for key, value in row.items():
                if "leave" in key.lower():
                    try:
                        total_leave += float(value)
                    except (ValueError, TypeError):
                        pass

    with open(args.output, "w", encoding="utf-8") as file:
        file.write("HR Leave Summary\n")
        file.write("================\n")
        file.write(f"Employees: {employee_count}\n")
        file.write(f"Total Leave: {total_leave:g}\n")


if _name_ == "_main_":
    main()
