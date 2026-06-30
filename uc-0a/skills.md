skills:
  - name: classify_complaint
    description: >
      Classify a single citizen complaint row into category, priority, reason, and flag
      using exact schema enforcement from the project README.
    input: >
      dict with keys: complaint_id (str), description (str).
    output: >
      dict with keys: complaint_id, category, priority, reason, flag.
      category is one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage,
      Heritage Damage, Heat Hazard, Drain Blockage, Other.
      priority is one of: Urgent, Standard, Low.
      reason is a one-sentence justification citing words from the description.
      flag is NEEDS_REVIEW or blank.
    error_handling: >
      If the description is empty or missing, set category to Other, priority to Low,
      reason to "No description provided", and flag to NEEDS_REVIEW. Never crash.

  - name: batch_classify
    description: >
      Read an input CSV of complaints, apply classify_complaint to every row,
      and write the results to an output CSV.
    input: >
      Path to a CSV file with columns: complaint_id, description.
    output: >
      Path to write a CSV file with columns:
      complaint_id, category, priority, reason, flag.
    error_handling: >
      If a row is malformed, skip it, log a warning, and continue processing other rows.
      Always produce output even if some rows fail. Never halt on a single bad row.
