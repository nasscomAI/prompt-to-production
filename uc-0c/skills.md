skills:
  - name: load_dataset
    description: Reads the provided local CSV file, validates columns, and reports the null count and specific rows with missing actual_spend before returning the data.
    example_invocation:
      call: `load_dataset({"file_path": "../data/budget/ward_budget.csv"})`
      returns: `"Loaded 300 rows. WARNING: 5 deliberately null 'actual_spend' values detected in the following rows: [...]"`
    input: The system file path string pointing to the targeted budget CSV dataset.
    output: A verified structured table reflecting the dataset alongside an upfront warning text module listing the detected null rows mapping.
    error_handling: System halt and raise FileNotFoundError if the dataset isn't accessible.

  - name: compute_growth
    description: Calculates the specified growth percentage between periods exclusively for a single ward and category without aggregating.
    example_invocation:
      call: `compute_growth({"ward": "Ward 1 – Kasba", "category": "Roads & Pothole Repair", "growth_type": "MoM"})`
      returns: `"2024-07 | 19.7 | +33.1% | Formula used: (19.7 - 14.8)/14.8"`
    input: A dictionary payload containing 'ward', 'category', and 'growth_type'.
    output: A multi-row table format listing Period, Actual Spend, computed Growth %, and the explicitly declared mathematical Formula utilized.
    error_handling: Strictly refuse execution if 'growth_type' is empty or if cross-ward aggregation is attempted.
