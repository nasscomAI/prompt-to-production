# skills.md — UC-0C Skills
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates schema and column types, and detects/reports all null actual_spend rows with reasons from notes.
    input: Path to the input budget CSV file (string).
    output: Tuple or dict of parsed row dictionaries, dataset metadata, and a list of detected null entries.
    error_handling: If required columns (`period`, `ward`, `category`, `actual_spend`) are missing or file cannot be opened, raise a descriptive ValidationError.

  - name: compute_growth
    description: Computes per-period growth (e.g. MoM) for a specific ward and category, returning an itemized table with formulas shown and null rows flagged.
    input: Filtered rows for a specific ward and category, and a required growth_type ("MoM" or "YoY").
    output: List of output records containing period, ward, category, actual_spend, growth_rate, formula, and status/notes.
    error_handling: If growth_type is missing or invalid, or if all-ward/all-category aggregation is requested, refuse with an explicit error message. If a period's actual_spend or its base is null, flag as NULL without computing.

