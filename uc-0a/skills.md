# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint into a predefined taxonomy and priority level with a cited reason.
    input: A complaint description string.
    output: A JSON object or structured data containing category, priority, reason, and flag.
    error_handling: If the text is too short or ambiguous, defaults to category 'Other' and sets flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Orchestrates the classification of multiple complaints from an input CSV and writes results to an output CSV.
    input: Input CSV file path containing complaint descriptions.
    output: Output CSV file path containing categorized and prioritized complaints.
    error_handling: Validates CSV structure; if a row fails classification, it is flagged for review rather than stopping the batch process.
