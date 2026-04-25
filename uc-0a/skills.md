# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into an exact category, determines priority based on severity keywords, provides a one-sentence reason citing the description, and flags ambiguous inputs.
    input: Dictionary representing one complaint row (e.g., containing 'complaint_id' and 'description').
    output: Dictionary with keys 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    error_handling: If genuinely ambiguous, sets 'flag' to 'NEEDS_REVIEW' and 'category' to 'Other'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: input_path - "../data/city-test-files/test_[your-city].csv" to CSV, output_path "/results_[your-city].csv" for CSV.
    output: Writes a CSV file containing classification results.
    error_handling: Flags nulls, skips or safely handles bad rows without crashing, ensuring output is produced even if some rows fail.
