skills:
  - name: classify_complaint
    description: Evaluates a single citizen complaint description and assigns a category, priority, reason, and review flag.
    input: A single string containing the citizen complaint description.
    output: A structured object with fields - category (string), priority (string), reason (string, one sentence citing specific words), and flag (string or blank).
    error_handling: If the complaint is genuinely ambiguous, assigns category "Other" and flag "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads a CSV file of citizen complaints, applies classify_complaint to each row, and writes the classified results to an output CSV.
    input: Path to an input CSV file containing citizen complaints (e.g. ../data/city-test-files/test_kolkata.csv).
    output: Path to an output CSV file containing the original data appended with category, priority, reason, and flag columns (e.g. results_kolkata.csv).
    error_handling: If input rows are malformed or missing required description fields, skips the row and logs a warning or outputs a blank classification with flag "DATA_ERROR".
