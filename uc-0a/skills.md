# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classify one complaint.
    input: Complaint row from CSV.
    output: Category, priority, reason and flag.
    error_handling: Return Other with NEEDS_REVIEW.

  - name: batch_classify
    description: Process an entire CSV file.
    input: Input CSV.
    output: Output CSV.
    error_handling: Skip invalid rows without crashing.
