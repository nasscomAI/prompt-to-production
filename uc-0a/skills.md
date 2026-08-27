# skills.md

skills:
  - name: classify_complaint
    description: Processes a single citizen complaint to output its categorized schema based on strictly allowed categories and severity keywords.
    input: A single citizen complaint row's description text.
    output: A structured return with fields for category, priority, reason, and flag.
    error_handling: If the input is genuinely ambiguous and does not fit known definitions, it sets the category to 'Other' and the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, applies the classify_complaint skill to each row, and writes the aggregated results to an output CSV.
    input: The file path to the input CSV file (e.g., ../data/city-test-files/test_[your-city].csv).
    output: The file path to the generated output CSV file (e.g., uc-0a/results_[your-city].csv).
    error_handling: Continues processing remaining rows if a malformed row is encountered, maintaining the same output structure for valid rows.
