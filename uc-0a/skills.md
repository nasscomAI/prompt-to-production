# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single complaint description to determine its category and priority based on defined rules.
    input: Dictionary/Object containing complaint description.
    output: Dictionary/Object with category, priority, reason, and flag fields.
    error_handling: Default to category 'Other' and 'NEEDS_REVIEW' flag for critically underspecified descriptions.

  - name: batch_classify
    description: Automates the classification process for an entire dataset, from input CSV to output CSV.
    input: Path to an input CSV file containing citizen complaints.
    output: Path to an output CSV file with results in the mandated schema.
    error_handling: Continues processing if individual rows fail, logging specific errors for review.
