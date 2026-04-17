# skills.md — UC-0C Financial Data Analyst Skills

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates expected columns, and explicitly flags any null 'actual_spend' values by reporting their count and specific row details.
    input: File path to the dataset CSV file (e.g., `../data/budget/ward_budget.csv`).
    output: A validated data object containing the parsed rows, alongside a strict audit report identifying any null values and their corresponding 'notes'.
    error_handling: Throws a schema validation error if columns are missing; explicitly refuses to proceed with silent null dropping if missing data is detected.

  - name: compute_growth
    description: Calculates the requested growth metric over time for a targeted ward and category, explicitly documenting the formula used for each computed row.
    input: The validated dataset, specific filters (ward, category), and the exact `growth_type` (e.g., 'MoM').
    output: A per-period table (e.g., a structured CSV or list of dictionaries) containing the period, actual spend, computed growth metric, and the mathematical formula used.
    error_handling: Immediately halts and refuses execution if `growth_type` is missing or if the request attempts to aggregate metrics across multiple distinct wards or categories.
