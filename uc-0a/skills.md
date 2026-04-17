skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into predefined category, priority, reason, and flag fields.
    input: Unstructured string containing the citizen complaint description.
    output: Structured fields mapping exactly the category, priority, reason, and flag.
    error_handling: If the text is genuinely ambiguous and taxonomy cannot be strictly determined, assigns the flag to NEEDS_REVIEW instead of generating false confidence.

  - name: batch_classify
    description: Reads an input CSV containing multiple citizen complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV.
    input: Path to the input CSV file containing raw complaint descriptions.
    output: A freshly written output CSV file with identical rows alongside filled category, priority, reason, and flag columns.
    error_handling: If an individual row encounters an error during processing, logs the error and continues to the next row to ensure the complete batch process executes.
