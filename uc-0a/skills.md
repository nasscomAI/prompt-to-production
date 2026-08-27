skills:
  - name: classify_complaint
    description: Classifies one citizen complaint into a category and priority with a reason and review flag.
    input: One complaint row containing a complaint description as text.
    output: A classification containing category, priority, reason, and flag.
    error_handling: If the description is genuinely ambiguous, use category Other and flag NEEDS_REVIEW; do not invent a category.

  - name: batch_classify
    description: Reads complaint rows from an input CSV, classifies each row, and writes the classification results to an output CSV.
    input: CSV file containing complaint rows with complaint descriptions and without category and priority_flag columns.
    output: CSV file containing the original complaint data with classification fields category, priority, reason, and flag.
    error_handling: Invalid or unusable complaint descriptions must be handled without inventing facts; genuinely ambiguous rows must use Other and NEEDS_REVIEW.