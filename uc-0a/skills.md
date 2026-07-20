# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and review flag based on the complaint description text.
    input: >
      A dictionary (dict) representing one CSV row with keys: complaint_id, date_raised,
      city, ward, location, description, reported_by, days_open. The 'description' field
      is the primary input for classification.
    output: >
      A dictionary (dict) with keys:
        - complaint_id (str): carried forward from input
        - category (str): exactly one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
        - priority (str): one of Urgent, Standard, Low
        - reason (str): one sentence citing specific words from the description
        - flag (str): "NEEDS_REVIEW" if category is ambiguous, otherwise empty string
    error_handling: >
      If description is empty, null, or not a string, return category "Other", priority "Low",
      reason "Description insufficient for classification", flag "NEEDS_REVIEW".
      If description does not match any known category pattern, return category "Other",
      priority "Standard", reason citing what was found, flag "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, applies classify_complaint to each row, and writes the classified results to an output CSV file.
    input: >
      Two string arguments:
        - input_path (str): file path to a CSV with columns complaint_id, date_raised, city, ward, location, description, reported_by, days_open
        - output_path (str): file path where the results CSV will be written
    output: >
      A CSV file written to output_path with columns: complaint_id, category, priority, reason, flag.
      One row per input complaint. Returns nothing (writes to disk).
    error_handling: >
      If input file does not exist or is unreadable, raise FileNotFoundError with a clear message.
      If a row fails classification (e.g., malformed data), log the error, write the row with
      category "Other", priority "Low", reason "Row processing failed", flag "NEEDS_REVIEW",
      and continue processing remaining rows. Never crash mid-batch — always produce partial
      output even if some rows fail.
