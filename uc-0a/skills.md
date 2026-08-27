skills:
  - name: classify_complaint
    description: Evaluates a single citizen complaint description to determine its category and priority level.
    input: A single string or data row representing the raw text of a citizen complaint.
    output: A structured object returning `category`, `priority`, a one-sentence `reason`, and an optional `flag`.
    error_handling: If the complaint cannot be confidently categorized from the text alone, returns `category: Other` and `flag: NEEDS_REVIEW`.

  - name: batch_classify
    description: Reads an input CSV dataset, applies classify_complaint sequentially to each row, and exports the results to an output CSV.
    input: A file path to the input CSV containing citizen complaint records (e.g., ../data/city-test-files/test_[city].csv).
    output: An output CSV file with the original data plus the predicted category, priority, reason, and flag fields.
    error_handling: If a row throws an exception or the input file format is malformed, log the error, assign a NEEDS_REVIEW flag for the failed row, and safely continue to the next.
