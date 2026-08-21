skills:
  - name: classify_complaint
    description: Classifies one complaint row into UC-0A outputs: category, priority, reason, and flag.
    input: A complaint row object or dictionary with at least the complaint text description and row metadata.
    output: A dict/object with fields {category, priority, reason, flag}.
    error_handling: If the complaint text is missing or ambiguous, return category Other, priority Standard, flag NEEDS_REVIEW, and a reason citing the unclear text.

  - name: batch_classify
    description: Reads an input complaint CSV, applies classify_complaint to every row, and writes results to an output CSV.
    input: An input CSV file path and an output CSV file path.
    output: A CSV file containing the original complaint rows plus category, priority, reason, and flag columns.
    error_handling: For malformed rows, preserve row order, set category to Other with NEEDS_REVIEW, provide a reason, and continue processing remaining rows.
