skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates columns, and reports any null counts and the specific rows affected before returning the loaded data.
    input: File path to the CSV dataset (e.g., ../data/budget/ward_budget.csv).
    output: Validated dataset structure with an explicit report of missing actual_spend rows.
    error_handling: Halts if required columns are missing and flags rows containing nulls directly to the user.

  - name: compute_growth
    description: Takes the ward, category, and growth_type, and calculates growth returning a per-period table with explicit formulas shown alongside results.
    input: Validated dataset, target ward, target category, and specific growth type (e.g., 'MoM').
    output: A per-period table containing the computed growth and the specific formula used for each row.
    error_handling: Refuses to compute if growth_type is missing/invalid. Explicitly flags outputs if required data points (like current or previous period) are null.
