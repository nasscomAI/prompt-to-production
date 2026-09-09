skills:
  - name: classify_complaint
    description: Classifies one citizen complaint into an approved category and priority, provides a one-sentence reason citing specific complaint words, and flags genuine ambiguity.
    input: One complaint row containing a complaint description.
    output: category, priority, reason, and flag.
    error_handling: If the category is genuinely ambiguous, set flag to NEEDS_REVIEW. Never invent a category or information.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every complaint row, and writes the classified results to an output CSV.
    input: CSV file containing citizen complaint descriptions.
    output: CSV containing the original complaint information plus category, priority, reason, and flag.
    error_handling: If the input file is missing, unreadable, or required complaint data is unavailable, report the error and do not guess.