skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag using the enforcement rules in agents.md.
    input: dict (one CSV row) with at least a `complaint_id` and `description` field.
    output: dict with keys complaint_id, category, priority, reason, flag.
    error_handling: If description is empty/missing, returns category "Other", priority "Low", flag "NEEDS_REVIEW" instead of raising. Never returns a category outside the allowed schema.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, and writes the results CSV with the original columns plus category/priority/reason/flag appended.
    input: input_path (str, path to test_[city].csv), output_path (str, path to write results_[city].csv).
    output: None — writes output_path to disk; prints a completion message.
    error_handling: If a single row raises an unexpected exception during classification, that row is caught, written with category "Other" / flag "NEEDS_REVIEW" and a reason explaining the failure, and the batch continues rather than aborting.
