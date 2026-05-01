# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and review flag.
    input: "Dict with keys: complaint_id (string), description (string)"
    output: "Dict with keys: complaint_id (string), category (string), priority (string), reason (string), flag (string or empty)"
    error_handling: "If description is null/empty, output all fields with flag=NEEDS_REVIEW. If description is ambiguous (two or more equally valid categories), output category=Other and flag=NEEDS_REVIEW. Never crash; always produce output row."

  - name: batch_classify
    description: Reads input CSV, classifies each complaint row using classify_complaint, writes results CSV with all rows including failures.
    input: "File path to input CSV with columns: complaint_id, description (category and priority_flag columns stripped)"
    output: "File path to output CSV with columns: complaint_id, category, priority, reason, flag"
    error_handling: "Flag null descriptions with NEEDS_REVIEW. Skip malformed rows with warning but continue processing. Always write output file even if some rows fail. Log summary of processed/flagged rows."
