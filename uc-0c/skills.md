skills:
  - name: load_dataset
    description: Reads the budget CSV, filters dynamically based on explicit target ward and category parameters to prevent silent aggregation, validates columns, and reports null count and context before returning data.
    input: String path to the input CSV, target_ward string, target_category string.
    output: List of dictionary records filtered precisely to the designated scope.
    error_handling: Refuses execution and fails completely if targets are missing or generic 'Any', rather than returning a flattened scope.

  - name: compute_growth
    description: Takes the pre-filtered ward data, parses chronological periods, and applies the explicit designated growth_type formula (MoM or YoY) calculating row values.
    input: List of dictionary dataset records and the chosen string growth_type.
    output: Processed list of dictionaries containing calculated fields and explicitly tagged formulas.
    error_handling: Handles explicitly NULL actual_spend rows by tagging 'Must be flagged — not computed', avoiding silent omission or erroneous division-by-zero math.
