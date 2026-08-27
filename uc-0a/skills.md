skills:
  - name: classify_complaint
    description: Classify a single citizen complaint description into predefined schema fields based on strict taxonomy and priority rules.
    input: String representing the text description of the complaint.
    output: Structured format comprising category, priority, reason, and flag fields.
    error_handling: If the complaint intent is completely unclear or crosses multiple categories indistinguishably, assign a predefined generic category (like Other) and strictly set the flag field to 'NEEDS_REVIEW'. Do not false guess with high confidence.

  - name: batch_classify
    description: Repeatedly applies the classify_complaint skill across an entire input CSV of citizen complaints to produce a result CSV with added classification columns.
    input: Filepath to an input CSV containing complaint rows (e.g., '../data/city-test-files/test_[your-city].csv').
    output: Filepath to an output CSV containing the original data with newly appended classification schema columns (e.g., 'results_[your-city].csv').
    error_handling: If input CSV is missing or empty, exit gracefully. If specific rows fail during extraction, either skip and log the error or leave output columns empty with flag 'NEEDS_REVIEW'.
