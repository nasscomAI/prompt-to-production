# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a category, priority, reason, and flag.
    input: dict with keys: complaint_id (str), description (str or null)
    output: dict with keys: complaint_id (str), category (str from allowed list), priority (Urgent/Standard/Low), reason (str), flag (NEEDS_REVIEW or blank)
    error_handling: If description is null/empty, return category: Other, priority: Low, reason: "No description provided", flag: NEEDS_REVIEW. If category is ambiguous, return category: Other with flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes a results CSV.
    input: CSV file path with columns: complaint_id, description (and optionally others to ignore)
    output: CSV file path with columns: complaint_id, category, priority, reason, flag
    error_handling: Skip malformed rows without crashing. Log errors but continue processing. Flag null/empty descriptions. Produce output file even if some rows fail.
