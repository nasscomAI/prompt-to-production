


skills:

name: load_dataset
description: Reads the budget CSV file, validates the required columns, and explicitly identifies rows with null actual_spend values before returning the data.
input:
type: string
format: File path to the input CSV dataset.
output:
type: object
format: Parsed dataset structure including a validation report of total null counts and the specific rows containing them.
error_handling: Halts execution if the file cannot be read or lacks required columns, and strictly surfaces all null actual_spend rows alongside their explanatory notes to prevent silent null handling.

name: compute_growth
description: Calculates the specified growth metric for a strictly defined ward and category over time, returning a per-period table with the explicit mathematical formula attached to each row.
input:
type: object
format: Parameters including the parsed dataset, target ward string, target category string, and a mandatory growth_type string.
output:
type: array
format: A detailed per-period table (array of objects) containing the period, calculated growth result, and the exact formula used for the calculation.
error_handling: Refuses execution and asks for clarification if growth_type is omitted to prevent formula assumption, rejects any attempt to aggregate across multiple wards or categories, and outputs a flagged status with the null reason instead of a calculated number for any period missing actual_spend data.