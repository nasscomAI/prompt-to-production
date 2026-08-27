skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to determine its category, priority level, and extraction-based reasoning.
    input: String containing the raw text description of a citizen complaint.
    output: Object containing category (String), priority (String), reason (String), and flag (String).
    error_handling: If input is ambiguous or does not fit standard allowed categories, defaults category to 'Other' and sets flag to 'NEEDS_REVIEW' to prevent false confidence.

  - name: batch_classify
    description: Reads an input CSV of complaints and sequentially applies the classify_complaint skill to each row, outputting the results.
    input: Filepath to an input CSV file containing complaint rows.
    output: Filepath to a generated output CSV file containing the classifications.
    error_handling: Handles malformed rows by skipping them or marking their output with 'NEEDS_REVIEW' and continues processing the remaining rows without crashing.
