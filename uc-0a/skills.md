# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one complaint record into an exact taxonomy category
      with priority, cited reason, and ambiguity flag.
    input: One dict representing a CSV row; must contain `description`
      (string); optionally `complaint_id`.
    output: Dict with keys `complaint_id`, `category` (one of Pothole,
      Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage,
      Heat Hazard, Drain Blockage, Other), `priority` (Urgent/Standard/Low),
      `reason` (single sentence citing words from the description),
      `flag` ("NEEDS_REVIEW" or empty).
    error_handling: If `description` is missing, blank, or malformed, returns
      category Other, priority Standard, flag NEEDS_REVIEW with an explanatory
      reason instead of raising. If two categories score equally, selects by
      fixed precedence order and sets NEEDS_REVIEW.

  - name: batch_classify
    description: Reads the input complaints CSV, applies classify_complaint to
      every row, and writes the results CSV.
    input: Two path strings — `input_path` to test_[city].csv (UTF-8, with a
      `description` column) and `output_path` for results_[city].csv.
    output: Writes results CSV with columns complaint_id, category, priority,
      reason, flag; returns a summary dict (total, urgent, needs_review,
      failed counts).
    error_handling: Missing/unreadable input file or absent `description`
      column exits cleanly with an ERROR message on stderr and exit code 1
      (no traceback). Any unexpected per-row exception is caught and emitted
      as an Other + NEEDS_REVIEW row so one bad row can never abort the batch;
      output file is always produced.
