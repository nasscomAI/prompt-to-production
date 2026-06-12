# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and reports the null count and affected rows before returning the parsed data.
    input: String input_path to the source CSV file.
    output: A list of dictionaries representing the parsed and validated dataset.
    error_handling: If the file is missing or malformed, raise an explicit error.

  - name: compute_growth
    description: Filters data for the specific ward and category, and calculates the specified growth_type (MoM/YoY) across periods.
    input: The parsed dataset, target 'ward', target 'category', and 'growth_type'.
    output: A list of dictionaries containing 'period', 'ward', 'category', 'actual_spend', 'growth_metric', 'formula', and 'flag'.
    error_handling: If 'ward', 'category', or 'growth_type' are missing, or if they imply aggregation (e.g., 'Any'), refuse execution. If 'actual_spend' is null for a period, output a flagged row with the note and skip computation.
