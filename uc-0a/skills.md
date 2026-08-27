skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag using strict RICE enforcement rules.
    input: dict with keys complaint_id (str), description (str) — all other fields are ignored during classification
    output: dict with keys complaint_id (str), category (str — exact allowed value), priority (str — Urgent/Standard/Low), reason (str — one sentence citing description words), flag (str — NEEDS_REVIEW or blank)
    error_handling: If description is empty or missing, output category=Other, priority=Low, reason="Description field is empty — cannot classify.", flag=NEEDS_REVIEW

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies classify_complaint to every row, and writes results to an output CSV.
    input: input_path (str — path to test_[city].csv), output_path (str — path to write results_[city].csv)
    output: CSV file written to output_path with columns complaint_id, category, priority, reason, flag; does not crash on bad rows — failed rows are written with flag=NEEDS_REVIEW and reason explaining the error
    error_handling: If a row fails to process, write it with category=Other, priority=Low, reason="Processing error: [error message]", flag=NEEDS_REVIEW and continue to the next row; print a summary count of failed rows at the end
