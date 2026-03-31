# skills.md — UC-0C Growth Calculator

skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count and which rows before returning
    input: Path to the input CSV file.
    output: A validated dataset object/dictionary along with a report of null values and affected rows.
    error_handling: System halts if required columns are missing or file is unreadable.

  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table with formula shown
    input: Filtered dataset, target ward, target category, and growth_type (e.g., MoM).
    output: A detailed per-period table showing actual spend, computed growth, and the formula used.
    error_handling: Returns flagged values if actual spend is null, and throws an error if growth_type is absent.
