# skills.md

skills:
  - name: classify_complaint
    description: Classify one complaint row into category, priority, reason, and flag per agents.md enforcement rules.
    input: dict with keys complaint_id, date_raised, city, ward, location, description, reported_by, days_open (one CSV row).
    output: dict with keys complaint_id, category, priority, reason, flag.
    error_handling: If description is missing/empty, output category=Other, priority=Standard, reason="description missing", flag=NEEDS_REVIEW — never raise, never crash the batch.

  - name: batch_classify
    description: Read an input CSV of complaint rows, apply classify_complaint to each, write a results CSV.
    input: input_path (str, path to test_[city].csv), output_path (str, path to write results CSV).
    output: None (side effect — writes output_path); prints a one-line summary count on completion.
    error_handling: A single malformed/unreadable row is caught, logged to stderr, and written to output with flag=NEEDS_REVIEW instead of aborting the whole batch — the run must always produce an output file with one row per input row.
