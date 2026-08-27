# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a predefined category, assigns priority, and provides a reason.
    input: A single citizen complaint row (dictionary/string) containing the description.
    output: A structured output containing the category, priority, reason, and flag.
    error_handling: If the complaint is genuinely ambiguous, the category is set to a best guess (or 'Other') and the flag is set to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes an output CSV.
    input: File path to the input CSV (e.g., ../data/city-test-files/test_pune.csv).
    output: Writes to an output CSV file (e.g., results_pune.csv).
    error_handling: Raises an error if the input file is not found. Logs an error and continues if a single row fails processing.
