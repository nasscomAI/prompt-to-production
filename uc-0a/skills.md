# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason and flag using deterministic keyword-family scoring.
    input: dict with at least complaint_id (string) and description (string); extra columns such as ward, location, days_open are ignored for classification.
    output: dict with keys complaint_id, category, priority, reason, flag — category is one of the 10 allowed strings, priority is Urgent/Standard/Low, flag is NEEDS_REVIEW or empty string.
    error_handling: empty/missing description or unrecognisable text returns category "Other", priority "Standard", flag "NEEDS_REVIEW", with a reason stating no classifiable signal was found; two category families tying at equal score returns the schema-order winner with flag "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads the city test CSV, applies classify_complaint to every row, and writes a results CSV with one output row per input row.
    input: filesystem paths — input_path to a UTF-8 test_[city].csv with a header row, output_path for results_[city].csv.
    output: CSV file with header complaint_id,category,priority,reason,flag and exactly one row per input complaint; also prints a per-batch tally (rows read, urgent count, flagged count, failures) to stdout.
    error_handling: missing input file exits with a clear error message before writing anything; a malformed individual row (short row, bad unicode) is written with category "Other" and flag "NEEDS_REVIEW" instead of aborting the batch; nulls in description are treated as empty text, never as crashes.
