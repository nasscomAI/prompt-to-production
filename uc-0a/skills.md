# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classify a single citizen complaint row into a structured output with
      category, priority, reason, and flag fields.
    input: >
      A dict (one CSV row) containing at minimum complaint_id (string) and
      description (free-text string).
    output: >
      A dict with keys: complaint_id (string), category (one of: Pothole,
      Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage,
      Heat Hazard, Drain Blockage, Other), priority (Urgent, Standard, or Low),
      reason (one sentence citing specific words from the description),
      flag (NEEDS_REVIEW if the category is genuinely ambiguous, blank otherwise).
    error_handling: >
      If the description is missing or empty, return category: Other,
      priority: Standard, reason: "No description provided", flag: NEEDS_REVIEW.
      If the description does not clearly map to a single category, set the
      best-match category (or Other) and flag: NEEDS_REVIEW. Priority must
      still be determined — if any severity keyword (injury, child, school,
      hospital, ambulance, fire, hazard, fell, collapse) is present, priority
      is Urgent regardless of ambiguity.

  - name: batch_classify
    description: >
      Read an input CSV of citizen complaints, apply classify_complaint to
      each row, and write the results to an output CSV.
    input: >
      input_path (string): absolute or relative path to a CSV file with
      columns complaint_id and description. output_path (string): path
      where the results CSV will be written.
    output: >
      A CSV file at output_path with columns: complaint_id, category,
      priority, reason, flag — one row per input complaint, in the same
      order as the input file.
    error_handling: >
      If a row fails to parse or classify_complaint raises an error, log the
      complaint_id and error, write that row with category: Other, priority:
      Standard, reason: "Row could not be parsed", flag: NEEDS_REVIEW, and
      continue processing remaining rows. The batch must never crash — partial
      output is better than no output. Null or missing description values must
      be flagged, not silently skipped.

