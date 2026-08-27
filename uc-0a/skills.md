skills:
  - name: classify_complaint
    description: Processes a single complaint description to extract structured classification data.
    input: One complaint row description text (string).
    output: A dictionary with keys 'category' (string), 'priority' (string), 'reason' (string, exactly one sentence), and 'flag' (string).
    error_handling: If the description is genuinely ambiguous, do not hallucinate; set flag exactly to 'NEEDS_REVIEW' to avoid false confidence.

  - name: batch_classify
    description: Reads an input CSV file, applies the classify_complaint skill to every row, and writes the results to an output CSV file.
    input: Input CSV file path (string).
    output: Output CSV file containing original rows plus the classification columns.
    error_handling: If the input file is not found, halt execution. If a specific row fails, log the error and continue processing the remaining rows.
