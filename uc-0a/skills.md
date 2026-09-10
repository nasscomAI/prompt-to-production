# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one complaint row into fixed category + priority + one-sentence quoted reason + review flag.
    input: A dict for one CSV row with at least `complaint_id` (string) and `description` (string).
    output: A dict with `complaint_id` (string), `category` (one of the 10 exact allowed strings), `priority` (Urgent | Standard | Low), `reason` (one sentence quoting 1–6 words from the description), `flag` (NEEDS_REVIEW or empty string).
    error_handling: On missing/blank description returns category Other, priority Standard, reason stating the description was blank, flag NEEDS_REVIEW. On any unexpected error returns category Other with flag NEEDS_REVIEW instead of raising, so the batch never crashes.

  - name: batch_classify
    description: Reads an input city CSV, applies classify_complaint to every row, writes results CSV.
    input: input_path (string path to test_[city].csv with complaint_id and description columns) and output_path (string path for results CSV).
    output: A CSV file with header complaint_id,category,priority,reason,flag — one row per input row, written even if individual rows fail.
    error_handling: Raises FileNotFoundError with a clear message if the input file is missing. Skips nothing silently: each bad row becomes an Other + NEEDS_REVIEW row. Never crashes on nulls, short rows, or encoding issues (reads UTF-8 with errors replaced).
