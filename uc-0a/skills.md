# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into category, priority, reason, and flag.
    input: A dictionary or JSON object with a "description" field (string) — the text of the citizen complaint.
    output: A dictionary or JSON object with fields: category (string), priority (string), reason (string), flag (string).
    error_handling: If the description is empty or cannot be classified, set category to "Other" and flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each row, and writes the output CSV.
    input: Path to input CSV file containing at least a "description" column. Rows must not have pre-existing "category" or "priority_flag" columns.
    output: Writes a CSV file with columns: category, priority, reason, flag — one row per input row in the same order.
    error_handling: If a row has a missing or empty description, classify it as category "Other", priority "Standard", reason "No description provided", flag "NEEDS_REVIEW". If the input file is missing columns or cannot be read, raise a clear error message.
