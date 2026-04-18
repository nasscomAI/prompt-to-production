# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single unstructured citizen complaint into a standard category, priority, and reason.
    input: A single complaint row containing the complaint description as a text string.
    output: A structured output containing category (string), priority (string), reason (string), and an optional flag (string).
    error_handling: Sets the 'flag' to 'NEEDS_REVIEW' and category to 'Other' if the complaint category is genuinely ambiguous or cannot be reliably determined.

  - name: batch_classify
    description: Reads a batch of citizen complaints from an input CSV file, applies the classifier to each row, and writes the results to an output CSV.
    input: Path to an input CSV file (e.g., `../data/city-test-files/test_[your-city].csv`).
    output: Writes out a formatted CSV file to the target output path (e.g., `uc-0a/results_[your-city].csv`) containing the classified rows.
    error_handling: Exits cleanly with an error message if the input CSV file cannot be found or read, and skips rows with completely invalid formatting.
