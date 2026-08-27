skills:

name: load_dataset
description: Reads the ward_budget CSV dataset, validates required columns, and identifies rows where actual_spend is null.
input: File path to a CSV dataset containing ward budget data with columns period, ward, category, budgeted_amount, actual_spend, and notes.
output: A validated dataset ready for analysis along with identification of rows containing null actual_spend values.
error_handling: If the file cannot be read or required columns are missing, return an error message and stop execution.

name: compute_growth
description: Calculates growth for a specific ward and category using the requested growth type and produces a per-period growth table including the formula used.
input: Dataset returned by load_dataset along with parameters ward, category, and growth_type.
output: A table containing period, actual_spend, computed growth value, the formula used, and notes for flagged rows.
error_handling: If growth_type is missing or if data for the requested ward/category does not exist, refuse computation and return an explanatory error message.
