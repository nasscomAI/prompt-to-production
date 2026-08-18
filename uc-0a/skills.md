# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and review flag using deterministic keyword rules.
    input: A dict representing one CSV row, including at minimum `complaint_id` and `description` (other columns are ignored for classification).
    output: A dict with keys complaint_id, category, priority, reason, flag — category from the allowed list, priority in {Urgent, Standard, Low}, reason a one-sentence string citing description words, flag "NEEDS_REVIEW" or "".
    error_handling: If `description` is missing/empty, return category "Other", priority "Standard", flag "NEEDS_REVIEW", and a reason noting the missing description. If no category keyword matches, return category "Other" with flag "NEEDS_REVIEW" rather than guessing.

  - name: batch_classify
    description: Read an input CSV, apply classify_complaint to every row, and write a results CSV.
    input: input_path (str) to the test_[city].csv, output_path (str) for the results file.
    output: Writes a CSV with header complaint_id,category,priority,reason,flag — one row per input row, in input order. Returns None.
    error_handling: Skips no rows — a row that raises during classification is written with category "Other", priority "Standard", flag "NEEDS_REVIEW", and a reason describing the failure, so output is always produced even if some rows are bad. Missing input file raises a clear FileNotFoundError before any work begins.
