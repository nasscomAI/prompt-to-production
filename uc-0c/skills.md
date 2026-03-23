# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads a CSV file, validates columns, and reports null count and which rows before returning data.
    input: Path to CSV file; string.
    output: Structured dataset with null row report and column validation.
    error_handling: Returns error if file missing, unreadable, or columns invalid; flags and reports nulls.

  - name: compute_growth
    description: Takes ward, category, and growth_type, returns per-period table with formula shown for each row.
    input: Dataset, ward name, category name, growth_type; structured input.
    output: Per-period table with actual spend, growth, and formula used.
    error_handling: Refuses and asks if growth_type not specified; returns error if input is incomplete or ambiguous; flags null rows and reports reasons.
