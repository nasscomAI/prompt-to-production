name: load_dataset
description: Reads the CSV data, validates the expected columns, and reports the null count and specific null rows before returning the dataset.
input:
type: string
format: File path to the CSV dataset
output:
type: object
format: Validated data object containing the parsed rows and a validation report of null actual_spend rows
error_handling: Halts execution if expected columns are missing or improperly formatted, and explicitly throws an error to prevent silent null handling if it fails to identify the deliberately blank rows.

name: compute_growth
description: Computes the explicitly requested growth type for a distinct ward and category, outputting a per-period table that reveals the formula used for every row.
input:
type: object
format: Key-value parameters containing ward (string), category (string), and growth_type (string, e.g., MoM)
output:
type: file
format: Per-ward per-category CSV table displaying period, actual spend, computed growth, the explicit formula used, and missing data flags
error_handling: Refuses to execute and prompts the user if growth_type is missing, strictly refuses and alerts if asked to aggregate across multiple wards or categories, and replaces computation with a flagged note from the dataset for any row with a null actual_spend.