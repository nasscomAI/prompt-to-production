# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Given a single complaint row (dict), returns a dict with classification
      fields (complaint_id, category, priority, reason, flag). Uses keyword
      matching against the description to enforce the category taxonomy and
      severity rules. Never hallucinates sub-categories.
    input: >
      dict with keys: complaint_id, date_raised, city, ward, location,
      description, reported_by, days_open
    output: >
      dict with keys: complaint_id, category, priority, reason, flag
      category is one of: Pothole, Flooding, Streetlight, Waste, Noise,
      Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
      priority is: Urgent or Standard
      reason is a short sentence quoting words from the description
      flag is either NEEDS_REVIEW or empty string
    error_handling: >
      If description is missing or empty, return category: "Other",
      priority: "Standard", reason: "No description provided", flag: "NEEDS_REVIEW".
      Never raises an exception.

  - name: batch_classify
    description: >
      Reads an input CSV file, applies classify_complaint to every row, and
      writes a results CSV with columns: complaint_id, category, priority,
      reason, flag. Handles empty files, missing columns, and malformed rows
      without crashing.
    input: >
      input_path: str (path to test CSV), output_path: str (path to write results)
    output: >
      Writes a CSV file at output_path. Returns None.
    error_handling: >
      If input file is missing or unreadable, creates output with a single
      error row. If a row has missing fields, classifies with what is available
      and sets flag to NEEDS_REVIEW. Does not crash on bad rows — processes
      all rows independently.
