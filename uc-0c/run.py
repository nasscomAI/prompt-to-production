import app
import sys

# Test 2
sys.argv = ["app.py", "--input", "../data/budget/ward_budget.csv", "--ward", "Ward 1 – Kasba", "--category", "Roads & Pothole Repair", "--growth-type", "MoM", "--output", "growth_output.csv", "--mode", "rice"]
app.main()
print("RICE DONE")
