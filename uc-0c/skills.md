skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates its columns, and flags any null actual_spend rows with notes before returning the data.
    input: Path to budget CSV file (string).
    output: A list of dicts containing parsed rows, and a list of identified null rows with reasons.
    error_handling: Refuses and reports if the file is missing or contains invalid column headers.

  - name: compute_growth
    description: Computes MoM or YoY growth for a specific ward and category, returning a per-period table with formulas.
    input: Dictionary containing dataset, target ward (string), target category (string), and growth_type (string).
    output: Table containing period, budgeted_amount, actual_spend, growth_rate, formula, and notes.
    error_handling: Refuses and exits if growth_type is not provided or if all-ward aggregation is requested.
