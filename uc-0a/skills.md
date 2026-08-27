# skills.md

skills:
  - name: classify_complaint
    description: Receives one complaint row (description). Returns category, priority, reason, and flag based on schema.
    input: One complaint row with description field.
    output: A dictionary with category, priority, reason, and flag.
    error_handling: Set flag to NEEDS_REVIEW and category to Other if description is ambiguous or doesn't match predefined categories.

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint per row, and writes to output CSV.
    input: Input CSV path (e.g., test_pune.csv).
    output: Output CSV path (e.g., results_pune.csv).
    error_handling: Skips rows with missing descriptions or invalid data after logging errors.
