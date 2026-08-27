# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description to determine its category, priority, and a justification for the classification.
    input: A complaint description string or a data structure representing a single complaint row.
    output: A mapping containing category, priority, reason, and flag (NEEDS_REVIEW or blank).
    error_handling: Set flag to NEEDS_REVIEW and category to 'Other' if the classification is genuinely ambiguous or the input is insufficient for high-confidence mapping.

  - name: batch_classify
    description: Automates the processing of a batch of complaints from a CSV file, ensuring each row is classified according to the schema.
    input: Path to an input CSV file (e.g., test_[city].csv) and a target output path.
    output: A CSV file (e.g., results_[city].csv) containing the original data plus the four classification columns.
    error_handling: Skip or mark invalid CSV rows; ensure the process completes for all valid entries and produces a well-formatted output file.
