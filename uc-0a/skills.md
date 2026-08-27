# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag based on description text and severity keywords.
    input: A dictionary containing 'complaint_id' and 'description'.
    output: A dictionary with keys: 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    error_handling: Returns category 'Other' and flag 'NEEDS_REVIEW' for genuinely ambiguous or missing descriptions.

  - name: batch_classify
    description: Reads an input CSV from city-test-files, applies classify_complaint to each row, and writes the results to an output CSV.
    input: String paths for 'input_path' and 'output_path'.
    output: None (results are written to results_[city].csv).
    Input file: ` . ./data/city-test-files/test*[city].csv'
Output file: results\_[city]. csv
    error_handling: Flags null inputs, handles malformed rows gracefully, and ensures partial output if some rows fail.



