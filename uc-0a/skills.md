# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single raw citizen complaint description to assign a strict category, priority level, and reason.
    input: A single citizen complaint row/record containing the raw description text.
    output: A structured record containing exact fields for `category`, `priority`, `reason`, and `flag`.
    error_handling: If the category is genuinely ambiguous or cannot be determined from the description alone, outputs `category: Other` and sets the `flag` field to `NEEDS_REVIEW`.

  - name: batch_classify
    description: Reads a CSV file of citizen complaints, applies the `classify_complaint` skill to each row, and writes the complete results to an output CSV.
    input: File path to the input CSV containing citizen complaints (e.g., test_[city].csv).
    output: File path to the generated output CSV containing the classification results for all rows (e.g., results_[city].csv).
    error_handling: If the input file cannot be read, raises an error. If an individual row is malformed or causes an exception during classification, logs the error and continues to the next row, potentially marking the failed row's flag as ERROR.
