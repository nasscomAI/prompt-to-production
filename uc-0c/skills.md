skills:

name: load_dataset
description: Loads the ward budget dataset and validates required columns and null values.
input: Path to CSV dataset.
output: Parsed dataset with column validation and null row report.
error_handling: If required columns are missing or null rows are detected, report the rows and continue with flagged records.

name: compute_growth
description: Calculates growth for a specified ward and category based on the selected growth type.
input: Dataset, ward name, category name, and growth_type parameter.
output: Per-period growth table including formula used for each row.
error_handling: If actual_spend is null for a row, flag it and skip growth calculation.
