# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint into category, priority, reason, and flag
    input: A dictionary with keys: complaint_id (str), description (str)
    output: A dictionary with keys: complaint_id (str), category (str), priority (str), reason (str), flag (str)
    error_handling: If description is null or empty, set category to Other and flag to NEEDS_REVIEW. If description is ambiguous between categories, set flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Read an input CSV of complaints, classify each row using classify_complaint, and write results to an output CSV
    input: input_path (str) — path to CSV with columns complaint_id and description
    output: output_path (str) — path to write CSV with columns complaint_id, category, priority, reason, flag
    error_handling: Skip rows with missing complaint_id or description, log warnings, and continue processing. Produce output even if some rows fail. Never crash on bad rows.
