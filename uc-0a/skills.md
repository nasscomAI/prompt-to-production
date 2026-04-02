# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row, exacting category, priority, reason, and flag.
    input: A single citizen complaint containing description or other relevant details (String or Dict).
    output: A classified record including category, priority, reason, and flag (Dict or JSON).
    error_handling: Return category as 'Other' and set flag to 'NEEDS_REVIEW' if description is genuinely ambiguous.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies classify_complaint per row, and writes the results to an output CSV.
    input: Path to an input CSV file (e.g., ../data/city-test-files/test_[your-city].csv).
    output: Writes an output CSV file (e.g., results_[your-city].csv) and returns success status.
    error_handling: Skip malformed rows with warning; raise error if input file is missing or unreadable.
