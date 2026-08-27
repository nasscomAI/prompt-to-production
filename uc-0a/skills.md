skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a predefined category and priority, with a justified reason.
    input: Single complaint description, as a string.
    output: A dictionary containing category, priority, reason, and an optional flag.
    error_handling: If the complaint description is genuinely ambiguous, assigns category as Other and sets the flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, processes each row using classify_complaint, and writes the results to an output CSV.
    input: File path to the input CSV.
    output: File path to the newly written output CSV.
    error_handling: If the input file path is missing or invalid, halts execution. If an individual row classification fails unexpectedly, logs the error and continues.
