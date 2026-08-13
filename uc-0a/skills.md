skills:
  - name: classify_complaint
    description: Classifies one citizen complaint into an allowed category and priority with a one-sentence reason and review flag.
    input: One complaint row containing a description field.
    output: category, priority, reason, and flag.
    error_handling: If the category is genuinely ambiguous, use Other and set flag to NEEDS_REVIEW. Never invent a category or sub-category.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to every complaint row, and writes the classified results to an output CSV.
    input: CSV file containing complaint descriptions.
    output: CSV file containing the original complaint data plus category, priority, reason, and flag.
    error_handling: Process each valid row using the classification rules; for genuinely ambiguous complaints use Other and NEEDS_REVIEW, and do not invent missing categories.