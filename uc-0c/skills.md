# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: aggregate_numbers
    description: Aggregates numerical values from an input CSV by specified groupings (e.g., per-ward, per-category).
    input: Input CSV file path (string), grouping fields (list of strings).
    output: Aggregated CSV or dictionary with groupings and computed sums/counts.
    error_handling: If data is missing or ambiguous, flags the affected group for review and skips invalid rows.

  - name: validate_aggregation
    description: Validates that each number in the output is traceable to source rows in the input.
    input: Input CSV file path (string), output aggregation (CSV or dict).
    output: Validation report listing traceability and any discrepancies.
    error_handling: If traceability cannot be established, flags the value for review in the report.
