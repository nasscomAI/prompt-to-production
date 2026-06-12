skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into category, priority, justification, and ambiguity flag.
    input: A single string containing the text of the citizen complaint description.
    output: A dictionary containing category (string), priority (string), reason (string), and flag (string or empty).
    error_handling: If the complaint category is genuinely ambiguous or input is empty, sets category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads citizen complaints from an input CSV file, applies classify_complaint to each row, and writes the results to an output CSV file.
    input: Path to the input CSV file (e.g., test_[city].csv) containing a complaint description column.
    output: Path to the generated output CSV file (e.g., results_[city].csv) containing the classification columns.
    error_handling: Logs any rows with parsing issues, skips corrupted records, and sets flag to 'NEEDS_REVIEW' for failures.
