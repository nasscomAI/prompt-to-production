skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description and maps it to a standard category, priority, reason, and flag.
    input: A single citizen complaint row/description (string or object format).
    output: A structured record containing category, priority, reason, and flag (JSON or dictionary format).
    error_handling: Returns category as "Other" and sets flag to "NEEDS_REVIEW" if the input is completely ambiguous or unrecognizable.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: The file path to the input CSV containing citizen complaints (e.g., ../data/city-test-files/test_[city].csv).
    output: The file path to the generated output CSV (e.g., results_[city].csv) populated with classification columns.
    error_handling: Handles broken rows by skipping or marking them with an error state, logging the failure, and continuing to process the remaining rows.

example of the final command: 
python classifier.py \
  --input ../data/city-test-files/test_pune.csv \
  --output results_pune.csv