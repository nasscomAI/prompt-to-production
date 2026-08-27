# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and detects/reports any rows with null actual_spend before returning the data.
    input: File path to the budget CSV.
    output: A list of row dictionaries. Prints a report of the null count and the specific rows/reasons to standard error.
    error_handling: If the file does not exist or is missing required columns, raise an error.

  - name: compute_growth
    description: Computes the specified growth metric for a strictly filtered ward and category. Refuses aggregation.
    input: List of dataset rows, target ward (string), target category (string), and growth_type (string, e.g., 'MoM').
    output: A list of dictionaries representing the per-period result, including the actual spend, computed metric, formula used, and any flags for nulls.
    error_handling: If ward or category is missing or 'Any', refuse the calculation. If growth_type is missing, refuse the calculation. If a period's previous period is null, flag the result as cannot compute due to null.
