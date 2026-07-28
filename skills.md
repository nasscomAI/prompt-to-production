# skills.md

skills:
  - name: classify_complaint
    description: >
      Classify a single citizen complaint into an allowed category, priority,
      one-sentence reason, and optional NEEDS_REVIEW flag.
    input: >
      A dict with keys: complaint_id, description, days_open. The description
      field contains the citizen's plain-text complaint.
    output: >
      A dict with keys: complaint_id, category, priority, reason, flag.
      category is one of: Pothole, Flooding, Streetlight, Waste, Noise,
      Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
      priority is Urgent, Standard, or Low. flag is NEEDS_REVIEW or blank.
    error_handling: >
      If description is missing or empty, output category: Other,
      priority: Low, flag: NEEDS_REVIEW, reason: 'No description provided.'
      Never hallucinate category when evidence is absent.

  - name: batch_classify
    description: >
      Read an input CSV of citizen complaints, apply classify_complaint
      to every row, and write the results to an output CSV.
    input: >
      Path to a CSV file with header row including complaint_id, description,
      days_open (and optionally other fields which are ignored).
    output: >
      Writes a CSV file at the given output path with columns:
      complaint_id, category, priority, reason, flag. One row per input row.
    error_handling: >
      If a row has missing or malformed fields, still produces a row with
      category: Other, flag: NEEDS_REVIEW. Does not crash on bad rows.
      Writes partial output even if some rows fail.
