# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classify a single citizen-complaint row into the UC-0A schema
      (category, priority, reason, flag) using only the complaint
      description and the fixed taxonomy defined in agents.md.
    input: >
      A dict representing one CSV row. Required key: `description`
      (str, free text). Optional keys: `complaint_id` (str) and any
      metadata columns from the input CSV, which are passed through
      but not used for classification.
    output: >
      A dict with keys:
        complaint_id (str, passed through),
        category (str, exactly one of the ten allowed labels),
        priority (str, one of: Urgent, Standard, Low),
        reason   (str, a single sentence citing specific words from the description),
        flag     (str, either "NEEDS_REVIEW" or "").
    error_handling: >
      - Missing/empty description → category: Other, priority: Standard,
        flag: NEEDS_REVIEW, reason: "description missing or empty".
      - Ambiguous description (fits multiple categories or none cleanly)
        → category: Other, flag: NEEDS_REVIEW, reason cites the
        conflicting or insufficient words.
      - Severity keyword present (injury, child, school, hospital,
        ambulance, fire, hazard, fell, collapse) → priority is forced
        to Urgent regardless of category certainty.
      - Never raises; never returns a category outside the allowed set.

  - name: batch_classify
    description: >
      Read an input CSV of complaints, apply classify_complaint to each
      row, and write a results CSV with the same row count and the
      UC-0A output schema.
    input: >
      input_path (str): path to a CSV containing at minimum a
      `description` column (and typically a `complaint_id` column).
      output_path (str): path where the results CSV will be written.
    output: >
      Writes a CSV to output_path with columns:
      complaint_id, category, priority, reason, flag.
      Row count in output equals row count in input.
      Returns None.
    error_handling: >
      - Per-row failures are caught: a failing row is still written
        with category: Other, priority: Standard, flag: NEEDS_REVIEW,
        and a reason noting the failure — the job never aborts mid-file.
      - Null or missing fields are logged and flagged, not dropped.
      - If input_path cannot be opened, raise a clear FileNotFoundError
        before any output is written.
      - Output is written atomically where possible (write then rename)
        so partial runs do not corrupt a previous results file.
