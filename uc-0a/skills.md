# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify one complaint into category + priority with a cited reason and ambiguity flag.
    input: >
      A dict for one CSV row. Only `complaint_id` and `description` are required;
      other columns are passed through untouched.
    output: >
      A dict with keys complaint_id, category, priority, reason, flag.
      category ∈ the 10-item taxonomy; priority ∈ {Urgent, Standard, Low};
      reason is one sentence quoting matched words; flag ∈ {NEEDS_REVIEW, ""}.
    error_handling: >
      Empty/missing description → category Other, flag NEEDS_REVIEW. No keyword
      match or a tie between categories → best guess + flag NEEDS_REVIEW. Never raises.

  - name: batch_classify
    description: Apply classify_complaint to every row of an input CSV and write a results CSV.
    input: input_path (test_[city].csv) and output_path (results_[city].csv).
    output: >
      Writes results_[city].csv = original 8 columns + category, priority, reason,
      flag. Returns the output path and prints a processed/flagged count.
    error_handling: >
      Tolerates malformed rows by flagging them NEEDS_REVIEW and continuing, so a
      single bad row never aborts the batch; partial output is always produced.
