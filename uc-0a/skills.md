# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint description into a specific category and priority level, providing a justification and flagging ambiguity.
    input: A single complaint row or description string.
    output: A structured object containing: category, priority, reason, and flag.
    error_handling: If the description is genuinely ambiguous, set category to 'Other' and set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Orchestrates the classification process for an entire dataset by reading an input CSV and writing the results to an output CSV.
    input: Path to an input CSV file containing raw complaint descriptions.
    output: Path to an output CSV file with classified data (category, priority, reason, flag columns added).
    error_handling: Log any rows that fail classification and ensure the output file matches the expected schema even if some rows are ambiguous.
