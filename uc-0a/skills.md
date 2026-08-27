# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority,
      reason, and ambiguity flag using keyword-based enforcement rules.
    input: >
      dict row with keys: complaint_id (str), description (str), and other fields
      (date_raised, city, ward, location, reported_by, days_open — unused in classification)
    output: >
      dict with keys:
        complaint_id (str) — copied from input unchanged
        category (str) — exactly one of the 10 allowed values
        priority (str) — "Urgent" or "Standard"
        reason (str) — one sentence citing specific words from the description
        flag (str) — "NEEDS_REVIEW" or blank string
    error_handling: >
      If description is empty or missing: category = Other, priority = Low,
        flag = NEEDS_REVIEW, reason = "No description provided."
      If an exception occurs during classification: returns Other / Low / NEEDS_REVIEW
        with reason explaining the failure; never crashes the batch.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each
      row, and writes the results to an output CSV.
    input: >
      input_path (str) — path to test_[city].csv with columns:
        complaint_id, date_raised, city, ward, location, description, reported_by, days_open
      output_path (str) — path where results CSV will be written
    output: >
      results_[city].csv written to disk with columns:
        complaint_id, category, priority, reason, flag
      Console summary: count classified, count errors
    error_handling: >
      Per-row exceptions are caught individually — a single bad row does not stop the batch.
      Errors are reported to stdout and the failing row is written with category = Other,
        flag = NEEDS_REVIEW, and the error message as the reason.
      File-not-found or missing-column errors exit with a descriptive message.
