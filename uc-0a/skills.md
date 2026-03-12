# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row into category, priority, reason, and flag.
    input: >
      A dictionary representing one CSV row with keys:
      complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: >
      A dictionary with keys:
      complaint_id (passthrough), category (one of 10 allowed values),
      priority (Urgent | Standard | Low), reason (one sentence citing description words),
      flag (NEEDS_REVIEW or empty string).
    enforcement:
      - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
      - "Priority is Urgent if description contains any severity keyword: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
      - "Reason must cite specific words from the description that justify the chosen category."
      - "Flag is NEEDS_REVIEW when description matches two or more categories; otherwise blank."
    error_handling: >
      If description is missing or empty, return category: Other, priority: Standard,
      reason: "No description provided", flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Read an input CSV of complaints, classify each row using classify_complaint, and write results to an output CSV.
    input: >
      input_path (str): path to the input CSV file with complaint rows.
      output_path (str): path to write the results CSV.
    output: >
      A CSV file at output_path with columns: complaint_id, category, priority, reason, flag.
      One row per input complaint. Console message confirming row count.
    enforcement:
      - "Must not crash on malformed rows — skip and log errors."
      - "Output CSV must contain all successfully classified rows even if some rows fail."
      - "Header row must be: complaint_id,category,priority,reason,flag."
    error_handling: >
      Wrap each row classification in try/except. Log failed rows to stderr.
      Always write output file even if some rows fail.
