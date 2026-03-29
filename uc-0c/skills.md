# Skills

## `load_dataset`
- **name**: `load_dataset`
- **description**: Reads the budget CSV file, validates its column structure, and systematically reports missing values before returning the dataset.
- **input**: File path (string, e.g., `../data/budget/ward_budget.csv`).
- **output**: A loaded tabular dataset (DataFrame/table) combined with a manifest reporting the total count of null `actual_spend` rows and explicitly listing which rows contain them.
- **error_handling**: Halts operation if the required dataset columns are missing, and strictly reports (rather than silently dropping or modifying) all null `actual_spend` rows to prevent silent data loss.

## `compute_growth`
- **name**: `compute_growth`
- **description**: Calculates the specified period-over-period budget growth metric strictly for a single ward and category while embedding the mathematical formula into each output row.
- **input**: `ward` (string), `category` (string), and `growth_type` (string, e.g., "MoM", "YoY").
- **output**: A per-period table strictly bounded to the requested ward and category, displaying computed growth along with a dedicated column explicitly showing the calculation formula used for every row.
- **error_handling**: Instantly refuses execution if `growth_type` is unspecified (never defaulting or guessing). Refuses operation if asked to aggregate data across multiple wards or categories without explicit instruction. Prevents "silent null handling" by actively flagging any periods with null `actual_spend` instead of calculating through them.
