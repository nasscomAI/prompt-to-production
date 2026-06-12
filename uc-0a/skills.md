# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single civic complaint row into a category, priority, reason, and review flag using keyword-based enforcement rules.
    input: A dict containing complaint fields — complaint_id (str), description (str), and optional metadata fields (city, ward, location, etc.).
    output: A dict with keys — complaint_id (str), category (str), priority (str), reason (str), flag (str, either "NEEDS_REVIEW" or "").
    error_handling: If description is missing or empty, returns category "Other", priority "Low", reason "No description provided", and flag "NEEDS_REVIEW". Never raises an exception on a bad row.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes a results CSV with classification columns appended.
    input: input_path (str) — path to a CSV file with columns including complaint_id and description; output_path (str) — path to write the results CSV.
    output: A CSV file at output_path containing all original columns plus category, priority, reason, and flag columns. Rows that fail to process are written with error values and flag "NEEDS_REVIEW".
    error_handling: Logs a warning for each row that raises an exception during processing; continues to process remaining rows and always writes an output file even if all rows fail.
