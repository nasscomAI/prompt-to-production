# skills.md — UC-0C Growth Calculator

skills:

  - name: load_dataset
    description: Reads the ward budget CSV, validates the required columns, and identifies all rows containing null actual_spend values before calculations are performed.
    input: Path to the ward budget CSV file.
    output: Validated dataset together with the null count, affected rows, and null reasons from the notes column.
    error_handling: If the file cannot be read, required columns are missing, or data cannot be parsed reliably, report the problem instead of guessing or silently modifying values.

  - name: compute_growth
    description: Calculates growth for one explicitly requested ward and category using the explicitly supplied growth type and returns a per-period table with the formula shown.
    input: Validated dataset, ward, category, and growth_type.
    output: Per-period growth results for the requested ward and category, including actual spend, growth result or null flag, and the formula used.
    error_handling: Refuse unspecified growth types or prohibited aggregation. If the current or comparison value required for a calculation is null, flag the calculation rather than substituting or guessing a value.