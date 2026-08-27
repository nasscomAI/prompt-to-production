skills:
  - name: classify_complaint
    description: Processes a single citizen complaint description and returns structured classification data including category, priority, reason, and an optional review flag.
    input: String containing one citizen complaint description.
    output: Structured object containing category (string), priority (string), reason (string), and flag (string or blank).
    error_handling: Return category as "Other" and set flag as "NEEDS_REVIEW" if the description is genuinely ambiguous or lacks necessary detail.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, applies the classify_complaint skill to each row, and writes the structured classification data to an output CSV file.
    input: Filepath to an input CSV (e.g., ../data/city-test-files/test_[your-city].csv).
    output: Filepath to the requested output CSV (e.g., uc-0a/results_[your-city].csv) populated with the 15 classified rows per city.
    error_handling: If a row fails to process or is ambiguous, apply the error handling from classify_complaint and continue processing the remaining rows without halting execution.
