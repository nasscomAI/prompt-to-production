skills:
  - name: classify_complaint
    description: Classify one citizen complaint into an allowed category and priority, provide a one-sentence reason citing specific words from the description, and set NEEDS_REVIEW when the category is genuinely ambiguous.
    input: One complaint row containing a complaint description.
    output: One classification containing category, priority, reason, and flag.
    error_handling: If the category is genuinely ambiguous, set flag to NEEDS_REVIEW and use only an allowed category; do not invent a sub-category.

  - name: batch_classify
    description: Read an input CSV, apply classify_complaint to each complaint row, and write the classified results to an output CSV.
    input: A CSV file containing complaint rows with category and priority_flag columns stripped.
    output: An output CSV containing the classification results for each row.
    error_handling: Handle invalid or ambiguous rows without crashing and preserve the required output fields.