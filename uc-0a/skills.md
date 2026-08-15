# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one complaint row into category + priority + reason + flag using the fixed taxonomy and severity keywords.
    input: dict — one CSV row keyed by header (complaint_id, description, ward, etc.)
    output: dict — keys complaint_id, category, priority, reason, flag
    error_handling: Missing/empty description returns category Other, priority Standard, flag NEEDS_REVIEW with an explanatory reason; unknown complaint_id falls back to ROW-UNKNOWN.

  - name: batch_classify
    description: Reads the input test_[city].csv, applies classify_complaint to every row, and writes the results CSV preserving all original columns plus category, priority, reason, flag.
    input: input_path (str), output_path (str)
    output: writes results_[city].csv; returns number of rows processed
    error_handling: Missing input file exits with an error message; malformed rows are caught per row and written as Other + NEEDS_REVIEW so the batch always completes.