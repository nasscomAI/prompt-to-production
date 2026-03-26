# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag based on the description.
    input: String representing the complaint description.
    output: Object containing category, priority, reason, and flag.
    error_handling: For ambiguous input, set flag to NEEDS_REVIEW and category to Other.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each row, and writes to an output CSV.
    input: Path to test_[city].csv.
    output: Path to results_[city].csv.
    error_handling: Logs row-level errors and continues processing.

