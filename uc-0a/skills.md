skills:
  - name: classify_complaint
    description: Analyzes one citizen complaint row to determine the exact category, assign priority based on severity keywords, provide a single-sentence reason citing specific words, and flag if genuinely ambiguous.
    input: One complaint row (string or dictionary) containing the description, with category and priority missing.
    output: A dictionary containing category (exact match from allowed list), priority (Urgent, Standard, Low), reason (one sentence), and flag (NEEDS_REVIEW or blank).
    error_handling: If classification fails, assign category to 'Other', priority to 'Standard', provide an error reason, and set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV containing citizen complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV.
    input: File path to the input CSV (e.g., ../data/city-test-files/test_[your-city].csv).
    output: File path to the output CSV (e.g., uc-0a/results_[your-city].csv).
    error_handling: Log errors for missing input files or inaccessible output paths. Skip or mark unparseable rows with errors and continue processing the rest of the batch.
