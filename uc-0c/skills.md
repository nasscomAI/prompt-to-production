# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates expected columns, and reports upfront on any null values before computation.
    input: File path to the budget dataset CSV (e.g., ../data/budget/ward_budget.csv).
    output: A validated dataset containing parsed rows, accompanied by a report detailing the count of null values in `actual_spend` and exactly which rows (with the `notes` column reason) are impacted.
    error_handling: Check if file exists. If core columns like `ward`, `category`, and `actual_spend` are missing, throw a structural error.

  - name: compute_growth
    description: Computes period-over-period financial growth strictly constrained to a single ward and category, displaying the exact formula used.
    input: The validated dataset, target ward, target category, and requested growth_type (e.g., MoM).
    output: A per-period table mapping the `period`, `actual_spend`, computed `growth`, and an explicit formula string (e.g., `(current - previous) / previous * 100`).
    error_handling: 
      - If --growth-type is absent or unrecognized, explicitly refuse to guess and output an error.
      - If told to aggregate across multiple wards/categories, refuse and abort.
      - If a row is flagged as null from the `load_dataset` step, flag the output row explicitly (e.g., "Must be flagged - not computed") rather than computing against 0.
