# skills.md

skills:
  - name: classify_complaint
    description: Analyzes one complaint row and outputs the category, priority, reason, and flag.
    input: A single row/string containing the citizen complaint description and relevant data.
    output: Structured data containing category, priority, reason, and flag.
    error_handling: If the complaint is genuinely ambiguous, the 'flag' field is set to "NEEDS_REVIEW" rather than forcing a confident classification.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies classify_complaint to each row individually, and writes the results to an output CSV.
    input: File path to the input CSV (e.g., ../data/city-test-files/test_[your-city].csv).
    output: File path to the output CSV (e.g., uc-0a/results_[your-city].csv).
    error_handling: Handles malformed rows gracefully and logs errors without stopping the batch processing.
