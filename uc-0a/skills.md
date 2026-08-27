skills:
  - name: classify_complaint
    description: Processes one complaint row to determine its category, priority, and reason.
    input: A representation of a single complaint row (e.g., text description).
    output: Structured data containing 'category', 'priority', 'reason' (one sentence with citations), and 'flag'.
    error_handling: If input text is genuinely ambiguous, assigns flag "NEEDS_REVIEW" and categorizes as appropriate.

  - name: batch_classify
    description: Reads an input CSV of city complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Input CSV file path (e.g., ../data/city-test-files/test_[city].csv).
    output: Output CSV file path containing the processed rows (e.g., results_[city].csv).
    error_handling: If a row is malformed or classification fails, skips or logs the anomaly while proceeding to the next row.
