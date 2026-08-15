skills:

  - name: classify_complaint
    description: Classify one citizen complaint into category, priority, reason, and review flag.
    input: One complaint row containing complaint_id and description.
    output: One classification containing complaint_id, category, priority, reason, and flag.
    error_handling: If the category is genuinely ambiguous, use Other and set flag to NEEDS_REVIEW without inventing information.

  - name: batch_classify
    description: Classify all complaint rows in an input CSV and write the classifications to an output CSV.
    input: CSV file containing complaint rows with complaint_id and description fields.
    output: CSV file containing the original complaint information plus category, priority, reason, and flag fields.
    error_handling: Process valid rows using the classification rules and use Other with NEEDS_REVIEW for genuinely ambiguous complaints.
