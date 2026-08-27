skills:
  - name: load_dataset
    description: Reads the budget CSV dataset, validates columns, and reports the null actual spend count along with details of the affected rows before returning.
    input: Path to the input CSV file as a string.
    output: A list of dictionaries representing the rows of the CSV, each containing keys like 'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', and 'notes'.
    error_handling: If any required columns are missing, raises a ValueError.

  - name: compute_growth
    description: Filters data by ward and category, then computes the period-over-period growth rates, showing the formula used and flagging nulls.
    input: A list of dicts from the dataset, the target ward as a string, the target category as a string, and the growth_type as a string.
    output: A list of dictionaries representing the per-period table with columns: Period, Actual Spend (₹ lakh), Growth, Formula, Notes.
    error_handling: Refuses calculation if growth_type is not specified, or if the target ward/category is null/empty or requests all-ward aggregation.
