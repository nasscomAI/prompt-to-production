# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:

  - name: classify_complaint
    description: >
      Classifies one complaint description into category, priority,
      reason, and flag based on municipal taxonomy rules.
    input: >
      Dictionary containing complaint_id and description.
    output: >
      Dictionary with complaint_id, category, priority, reason, flag.
    error_handling: >
      If description is missing or unclear return
      category = Other and flag = NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Reads a complaint CSV dataset, applies classification
      to each row, and writes results to a new CSV file.
    input: >
      Path to input CSV file.
    output: >
      CSV containing classification results.
    error_handling: >
      Any row that fails processing must still produce
      an output flagged NEEDS_REVIEW.