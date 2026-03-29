skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports null count and identifies which rows contain null actual_spend values with their notes before returning data.
    input: String (file path to the budget allocation CSV)
    output: Validated dataset structure (e.g., DataFrame), and a summary list of null rows containing the period, ward, category, and notes reason.
    error_handling: Fails and returns an error message if the file is missing, cannot be read, or if required columns are absent.

  - name: compute_growth
    description: Calculates specific growth metrics for a given ward and category over time, and returns a per-period table showing the formula used.
    input: Validated dataset structure, ward (string), category (string), and growth_type (string, e.g., 'MoM').
    output: Per-period table containing period, growth metric result, and the explicit formula used (e.g., ((current - previous) / previous) * 100).
    error_handling: Refuses calculation and prompts the user if growth_type is missing or invalid. Flags periods where actual_spend is null instead of computing.
