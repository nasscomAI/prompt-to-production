# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into the approved category and priority.
    input: A complaint record containing complaint_id and description.
    output: complaint_id, category, priority, reason, and flag.
    error_handling: If the complaint is ambiguous, assign category "Other" and set flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads all complaints from an input CSV file, classifies each complaint, and writes the results to an output CSV.
    input: Input CSV file path.
    output: Output CSV containing complaint_id, category, priority, reason, and flag.
    error_handling: Skip invalid rows, continue processing remaining rows, and record ambiguous complaints for review.