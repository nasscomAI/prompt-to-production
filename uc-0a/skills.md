
skills:
  - name: [skill_name]
    description: [One sentence — what does this skill do?]
    input: [What does it receive? Type and format.]
    output: [What does it return? Type and format.]
    error_handling: [What does it do when input is invalid or ambiguous?]

  - name: [second_skill_name]
    description: [One sentence]
    input: [Type and format]
    output: [Type and format]
    error_handling: [What does it do when input is invalid or ambiguous?]

# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag according to strict schema rules.
    input: Dictionary with complaint_id, description, and any relevant metadata fields from the input CSV.
    output: Dictionary with keys: complaint_id, category, priority, reason, flag.
    error_handling: If input is missing required fields or ambiguous, sets category to Other and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Processes an input CSV file, classifies each row, and writes results to an output CSV, handling errors gracefully.
    input: Input file path (string), output file path (string).
    output: Output CSV file with classified rows.
    error_handling: Flags nulls, does not crash on bad rows, produces output even if some rows fail.
