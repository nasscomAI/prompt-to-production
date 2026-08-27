skills:

name: load_dataset
description: Load the ward budget CSV dataset, validate required columns, and report null values before any computation.
input: Path to ward_budget.csv as a string file path.
output: Structured dataset containing rows of period, ward, category, budgeted_amount, actual_spend, and notes, along with a report of rows where actual_spend is null.
error_handling: If required columns are missing or the file cannot be read, return an explicit error and stop processing; if null values exist in actual_spend, report them and flag those rows before any growth calculation.

name: compute_growth
description: Calculate growth for a specific ward and category using the requested growth type (e.g., MoM) and return a per-period table with the formula shown.
input: Structured dataset from load_dataset plus parameters ward (string), category (string), and growth_type (MoM or YoY).
output: Table of periods for the selected ward and category containing period, ward, category, actual_spend, computed growth value, and the formula used for the calculation.
error_handling: If growth_type is missing or unsupported, refuse the request and ask for a valid type; if actual_spend is null for a period, flag the row and do not compute growth; if the request attempts aggregation across wards or categories, refuse rather than compute.

