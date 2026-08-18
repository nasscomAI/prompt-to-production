# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: compute_growth_table
    description: Computes per-ward, per-category MoM growth for actual_spend, handling nulls explicitly.
    input: The full ward_budget.csv file and parameters: ward, category, growth-type (MoM).
    output: A CSV table with columns: period, ward, category, MoM_growth, null_flag, null_reason.
    error_handling: If any row has a null actual_spend without a notes explanation, output NEEDS_REVIEW and specify which row failed.

  - name: validate_growth_output
    description: Validates the growth output for correct aggregation level, explicit null handling, and formula compliance.
    input: The growth_output.csv and the original ward_budget.csv.
    output: A report listing any aggregation errors, silent nulls, or formula mismatches.
    error_handling: If validation fails, output NEEDS_REVIEW and list discrepancies.
