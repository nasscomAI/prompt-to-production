skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports null count and which rows before returning.
    input: Filepath to the CSV dataset (String).
    output: Validated dataset structure and an explicit string reporting the count of null rows and displaying specific null rows with their notes.
    error_handling: Returns a clear error if columns are missing or file is unreadable.

  - name: compute_growth
    description: Takes ward, category, and growth_type, returns per-period table with formula shown.
    input: target ward (String), target category (String), and growth_type (String, e.g., MoM).
    output: Per-period table including actual spend, calculated growth, and an explicit formula column.
    error_handling: Refuse operation if growth_type is missing (do not guess). Refuse operation if system is asked to aggregate across all wards or all categories.
