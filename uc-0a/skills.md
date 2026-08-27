# skills.md

skills:
  - name: classify_complaint
    description: Classifies one citizen complaint row into a fixed category, priority, evidence-citing reason, and ambiguity flag.
    input: A dict representing one CSV row; only the `description` string (and `complaint_id` passthrough) is used.
    output: A dict with keys complaint_id, category, priority, reason, flag — category an exact allowed string, priority Urgent|Standard|Low (Urgent forced on severity keywords), reason exactly one sentence quoting description words, flag "" or NEEDS_REVIEW.
    error_handling: Missing/blank description → Other + NEEDS_REVIEW with a safe reason. LLM call failure after 3 retries → fallback row built deterministically (Other + NEEDS_REVIEW) so the function never raises.

  - name: batch_classify
    description: Reads the input complaints CSV, applies classify_complaint to every row, and writes the results CSV.
    input: Input path to test_[city].csv (header includes complaint_id and description) and output path for results_[city].csv.
    output: A results CSV with header complaint_id,category,priority,reason,flag containing one output row per input row; returns nothing but prints a completion summary.
    error_handling: Any unexpected per-row exception is caught and converted into a safe Other + NEEDS_REVIEW row instead of crashing; the output file is always written even if some rows fail.
