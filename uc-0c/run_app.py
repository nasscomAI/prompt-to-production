import sys
import os

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

import app

# Mock sys.argv
sys.argv = [
    "app.py",
    "--input", "../data/budget/ward_budget.csv",
    "--ward", "Ward 1 \u2013 Kasba", # \u2013 is the en-dash
    "--category", "Roads & Pothole Repair",
    "--growth-type", "MoM",
    "--output", "growth_output.csv"
]

if __name__ == "__main__":
    app.main()
