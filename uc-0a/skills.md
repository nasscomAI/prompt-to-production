skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint row and determines its appropriate category, priority, classification reason, and required review flag.
    input: A single row representing a citizen complaint, providing text description.
    output: A structured output containing category (string), priority (string), reason (string), and flag (string).
    error_handling: If the complaint text is too ambiguous to classify into an exact category, set category to 'Other' and set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Iterates through an input CSV file of complaint rows, applies the classify_complaint skill to each row, and produces an output CSV file with results.
    input: Path to an input CSV file containing citizen complaints (e.g., ../data/city-test-files/test_[your-city].csv).
    output: Writes a new CSV file (e.g., uc-0a/results_[your-city].csv) containing all original data plus the new category, priority, reason, and flag fields.
    error_handling: If the file is missing or unreadable, halt and surface a file reading error. If a row is malformed, skip or flag it and continue.
