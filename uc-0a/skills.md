skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a predefined category, priority, reason, and review flag.
    input: A single citizen complaint description string (from a CSV row).
    output: A structured record containing 'category', 'priority', 'reason' (one sentence citing specific words), and 'flag' ('NEEDS_REVIEW' or blank).
    error_handling: If the category is genuinely ambiguous or cannot be confidently determined from the description alone, set category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies the classify_complaint skill to each row iteratively, and writes the results to an output CSV.
    input: File paths for the input CSV (e.g., ../data/city-test-files/test_[city].csv) and output CSV (e.g., uc-0a/results_[city].csv).
    output: A processed CSV file written to the output path containing the new classification columns.
    error_handling: If a row is malformed or fails processing, log the error, skip or append an 'ERROR' marker for that row, and continue processing the remaining batch to ensure the pipeline does not halt.
