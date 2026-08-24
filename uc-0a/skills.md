# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies one complaint row into a category + priority + reason + flag decision
      following the exact classification schema.
    input: >
      A single dict / CSV row with a description field (str) and optional ward,
      location, reported_by fields.
    output: >
      A dict with exactly: complaint_id, category (one of: Pothole, Flooding,
      Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard,
      Drain Blockage, Other), priority (Urgent, Standard, Low), reason (one
      sentence citing words from description), flag (NEEDS_REVIEW or empty).
    error_handling: >
      If description is missing or empty, set category: Other, flag: NEEDS_REVIEW.
      If no allowed category clearly matches the description, set category: Other,
      flag: NEEDS_REVIEW and never invent sub-categories.

  - name: batch_classify
    description: >
      Reads an input CSV, applies classify_complaint to every row, and writes a
      results CSV containing the classification for each complaint.
    input: >
      Path to a CSV with columns complaint_id, description, and optional ward,
      location, reported_by.
    output: >
      A results CSV written to the output path with columns: complaint_id,
      category, priority, reason, flag — one row per input row.
    error_handling: >
      Never crashes on a bad row: wrap each row, classify it, and continue.
      If a row cannot be read or classified, emit category: Other, flag:
      NEEDS_REVIEW for that row and always produce the output file.
