name: "load_dataset"
description: "Reads the budget CSV, validates required columns and structure, and reports all null actual_spend rows with reasons before returning the dataset."
input:
type: "string"
format: "relative file path to CSV (../data/budget/ward_budget.csv)"
output:
type: "object"
format: "dataset with validated schema plus summary including total row count, column validation status, null_count, and detailed list of null rows (period, ward, category, notes)"
error_handling:
"If file path is invalid or file cannot be read — return error and stop execution"
"If required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing — return schema validation error"
"If column types or formats are incorrect (e.g., period not YYYY-MM) — return validation error"
"If dataset structure deviates from expected (e.g., missing months or wards) — return validation error"
"If null values exist in actual_spend — must explicitly report all such rows with period, ward, category, and notes; never silently ignore (prevents silent null handling failure)"
"If partial dataset loading or filtered loading is attempted — reject and require full dataset load (prevents wrong aggregation level issues)"
name: "compute_growth"
description: "Computes per-period growth for a specified ward and category using the given growth type, returning a detailed table with formulas and null handling."
input:
type: "object"
format: "validated dataset object, ward (string), category (string), growth_type (string: explicitly provided, e.g., MoM)"
output:
type: "table"
format: "per-period table with columns: period (YYYY-MM), ward (string), category (string), actual_spend (float or NULL), growth_value (percentage or NULL), formula_used (string), null_flag (boolean), null_reason (string from notes if applicable)"
error_handling:
"If ward or category is missing, invalid, or not found — return error and stop"
"If growth_type is not specified — refuse and request explicit input (prevents formula assumption failure)"
"If growth_type is ambiguous or unsupported — return error and do not assume"
"If operation attempts aggregation across wards or categories — refuse (prevents wrong aggregation level failure)"
"If actual_spend is null for any row — do not compute growth; flag row and include reason from notes (prevents silent null handling)"
"If prior period value required for growth is null or missing — flag and do not compute growth for that row"
"If output is not per-period per-ward per-category (e.g., single aggregated value) — reject as invalid output"
"If formula_used is missing in any row — reject output as invalid"
"If computed results contradict provided reference values where applicable — flag as error and halt output"