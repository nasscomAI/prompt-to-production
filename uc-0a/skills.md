# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single civic complaint row into category, priority, reason, and flag.
    input: Dict with at least a description field (string) and complaint_id field (string).
    output: Dict with keys — complaint_id (str), category (str), priority (str), reason (str), flag (str).
    error_handling: If description is empty, returns category Other, priority Low, flag NEEDS_REVIEW. If multiple categories match, sets flag NEEDS_REVIEW and picks the first match.

  - name: batch_classify
    description: Reads input CSV of complaints, applies classify_complaint to each row, writes results CSV.
    input: input_path (str) path to CSV with complaint rows, output_path (str) path to write results.
    output: CSV file with original columns plus category, priority, reason, flag appended.
    error_handling: Skips crash on bad rows — sets category Other, flag NEEDS_REVIEW and continues. Produces output file even if some rows fail.