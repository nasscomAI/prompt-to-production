import sys
from app import main

if __name__ == "__main__":
    sys.argv = ["app.py", "--input", "../data/budget/ward_budget.csv", "--ward", "Ward 4 – Warje", "--category", "Roads & Pothole Repair", "--growth-type", "MoM", "--output", "growth_output.csv"]
    main()
