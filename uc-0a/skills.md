# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:

  - name: classify_complaint
    description: >
      Classifies a single complaint description into category,
      priority, reason, and flag according to the municipal taxonomy.
    input: >
      Dictionary containing complaint_id and description fields.
    output: >
      Dictionary with complaint_id, category, priority, reason, flag.
    error_handling: >
      If description is missing or ambiguous return
      category = Other and flag = NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Reads complaint CSV file, applies classify_complaint to each row,
      and writes results to a new CSV file.
    input: >
      Path to input CSV file.
    output: >
      Output CSV containing classified complaints.
    error_handling: >
      If a row fails classification it should still produce
      an output row flagged NEEDS_REVIEW.
