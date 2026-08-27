skills:
  - name: classify_complaint
    description: >
      Classify a single citizen complaint row into a category, priority, reason,
      and optional flag based on keyword matching of the description field.
    input: >
      dict with keys: complaint_id, date_raised, city, ward, location,
      description, reported_by, days_open
    output: >
      dict with keys: complaint_id, category, priority, reason, flag.
      category must be one of: Pothole, Flooding, Streetlight, Waste, Noise,
      Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
      priority is Urgent if description contains any of: injury, child, school,
      hospital, ambulance, fire, hazard, fell, collapse; otherwise Standard.
      flag is "NEEDS_REVIEW" when the category is genuinely ambiguous, else "".
    error_handling: >
      If the description is missing or empty, return category: Other,
      priority: Standard, reason: "No description provided", flag: NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Read an input CSV of complaints, classify each row via classify_complaint,
      and write the results to an output CSV.
    input: >
      input_path (str) — path to a CSV with columns including 'description'
      and 'complaint_id'.
      output_path (str) — path where the results CSV will be written.
    output: >
      A CSV file at output_path with columns:
      complaint_id, category, priority, reason, flag.
    error_handling: >
      If a row cannot be parsed or classified, produce a fallback row with
      category: Other, priority: Standard, flag: NEEDS_REVIEW. Never crash
      on a bad row. Always write an output file even if some rows fail.
