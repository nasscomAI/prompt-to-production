# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: parse_budget_dataset
    description: Read and extract ward-level budget records from the CSV dataset.
    input: CSV dataset containing ward, category, and budget values.
    output: Structured list of records representing each ward and category budget entry.
    error_handling: If rows contain missing or invalid numeric values, flag them for review instead of discarding them.

  - name: validate_budget_scope
    description: Ensure that budget values remain scoped to the original ward and category without unintended aggregation.
    input: Parsed budget dataset records.
    output: Validated dataset ensuring numbers correspond exactly to the source records.
    error_handling: If aggregation across wards or categories is detected, stop processing and mark the output as NEEDS_REVIEW.