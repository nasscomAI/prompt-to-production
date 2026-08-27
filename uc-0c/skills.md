# skills.md
# UC-0C — Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and reports the null count and their reasons before returning.
    input: File path to CSV document (string).
    output: List of parsed rows and a list of flagged nulls.
    error_handling: If file is missing or unreadable, raise an error.

  - name: compute_growth
    description: Takes ward, category, and growth_type to calculate growth, returning a per-period table with formula shown.
    input: Ward string, Category string, Growth Type string, and dataset rows.
    output: CSV formatted table string containing growth and formulas.
    error_handling: Refuses if growth_type is missing or if asked to aggregate multiple wards without explicit permission.
