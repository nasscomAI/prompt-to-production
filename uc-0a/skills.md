# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category + priority, with a cited reason and optional flag.
    input: One CSV row as an ordered dict with at least complaint_id and description.
    output: A dict with keys complaint_id, category, priority, reason, flag (flag is NEEDS_REVIEW or blank).
    error_handling: If no severity keyword is found, priority falls back to Standard/Low by severity level. If the category is genuinely ambiguous, returns category: Other and flag: NEEDS_REVIEW rather than guessing.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to every row, and writes the results to an output CSV.
    input: input_path (path to test_[city].csv) and output_path (path to write results CSV).
    output: Writes results_[city].csv with header complaint_id, category, priority, reason, flag.
    error_handling: Does not crash on a bad or missing row — writes a flagged entry for that row and continues. Produces output even if some rows fail. Reports total rows processed and any rows flagged NEEDS_REVIEW.
