"""Helper script to run UC-0C with proper encoding for ward names."""
import subprocess
import sys

subprocess.run([
    sys.executable, "uc-0c/app.py",
    "--input", "data/budget/ward_budget.csv",
    "--ward", "Ward 1 \u2013 Kasba",
    "--category", "Roads & Pothole Repair",
    "--growth-type", "MoM",
    "--output", "uc-0c/growth_output.csv"
])
