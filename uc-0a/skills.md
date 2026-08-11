skills:
  - name: classify_complaint
    description: Classifies a single civic complaint row into category, priority, reason, and flag using deterministic keyword rules enforced by agents.md.
    input: A dict with keys — complaint_id (str), description (str). All other CSV fields are ignored by this skill.
    output: A dict with keys — complaint_id (str), category (str, one of 10 allowed values), priority (str, one of Urgent/Standard/Low), reason (str, one sentence quoting description words), flag (str, NEEDS_REVIEW or blank string).
    error_handling: If description is empty or None, set category=Other, priority=Low, reason='No description provided', flag=NEEDS_REVIEW. If description cannot be matched to any category, set category=Other and flag=NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV file of complaint rows, applies classify_complaint to each row, and writes a results CSV. Handles malformed rows without crashing.
    input: input_path (str, path to CSV file), output_path (str, path for results CSV). CSV must contain columns — complaint_id, description.
    output: A CSV file at output_path with columns — complaint_id, category, priority, reason, flag. One row per input complaint. Any rows that could not be processed include an error note in the reason field.
    error_handling: If a row is missing the complaint_id or description field, skip classification and write a row with flag=NEEDS_REVIEW and reason='Missing required field'. Log errors to stderr. Continue processing remaining rows — do not crash on a bad row.
