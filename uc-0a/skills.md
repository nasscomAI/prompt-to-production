# skills.md

skills:
  - name: classify_complaint
    description: Classifies one citizen complaint row into category, priority, reason, and flag per the RICE enforcement rules in agents.md.
    input: A dict for one row (must include complaint_id and description; other columns passed through untouched).
    output: A dict with keys complaint_id, category, priority, reason, flag — category from the fixed 10-value taxonomy, priority in {Urgent, Standard, Low}, reason a one-sentence citation of description words, flag either "NEEDS_REVIEW" or "".
    error_handling: If description is missing/empty, set category "Other", priority "Low", reason noting missing description, flag "NEEDS_REVIEW" — never raises, never skips the row.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, writes the results CSV with the four derived columns added.
    input: input_path (path to test_[city].csv), output_path (path to write results_[city].csv).
    output: Writes output_path as CSV: original columns plus category, priority, reason, flag. Returns nothing (or count of rows processed).
    error_handling: A malformed row (missing complaint_id, unreadable) is still written to output with flag NEEDS_REVIEW and a reason explaining the row-level failure — one bad row must never crash the batch or drop output for the rest.
