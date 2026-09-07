skills:
  - name: load_dataset
    description: Reads the ward budget CSV file, validates required columns, and identifies all rows with null or missing actual_spend values along with their notes before returning the dataset.
    input: File path string pointing to ward_budget.csv
    output: Dict/Dataframe containing validated rows, total row count, and a list of flagged null rows with period, ward, category, and notes reason.
    error_handling: Raises FileNotFoundError if CSV missing; flags missing actual_spend values and reports notes instead of silently skipping or imputing zeros.

  - name: compute_growth
    description: Calculates growth metrics for a specific ward and category over time according to the specified growth_type, outputting per-period results with explicit formulas shown.
    input: Target ward (string), target category (string), growth_type (string e.g. MoM/YoY), and validated dataset.
    output: Structured table containing period, actual_spend, computed growth percentage, formula string, and null flags.
    error_handling: Refuses calculation if ward or category is missing/unspecified (refuses all-ward aggregation); refuses calculation if growth_type is empty or ambiguous; flags null rows as NULL/UNCOMPUTED with reason.
