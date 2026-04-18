# skills.md
skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates expected columns, and reports the null count and specific rows with missing values before returning the loaded dataset.
    input: Filepath to the raw CSV budget dataset (string).
    output: A validated dataset containing the parsed rows, along with a report of null values and their corresponding 'notes'.
    error_handling: If required columns exist but contain nulls in 'actual_spend', flag them without terminating execution; if columns are entirely missing or the dataset is unreadable, raise a clear parsing error.

  - name: compute_growth
    description: Calculates period-over-period growth for a specific ward and category, returning a per-period table with the exact formula shown alongside the result.
    input: Validated dataset, target ward (string), target category (string), and specific growth_type (e.g., MoM or YoY).
    output: A per-period table displaying metrics, appending the exact exact formula used for calculation alongside the result for complete transparency.
    error_handling: Refuse to compute any global aggregation across wards or categories; if growth_type is missing, refuse and prompt the user; if division by zero occurs (e.g., previous period 'actual_spend' is 0), refuse calculation for that period and output a clear error message.
