# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into one of 10 categories with a priority level, a reason citing the description, and an optional review flag.
    input: >
      A dictionary (dict) representing one CSV row with keys:
      complaint_id (str), date_raised (str), city (str), ward (str),
      location (str), description (str), reported_by (str), days_open (int).
    output: >
      A dictionary with keys:
      complaint_id (str) — copied from input;
      category (str) — exactly one of: Pothole, Flooding, Streetlight, Waste,
        Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other;
      priority (str) — one of: Urgent, Standard, Low;
      reason (str) — one sentence citing specific words from the description;
      flag (str) — "NEEDS_REVIEW" if category is ambiguous or Other, else empty string.
    error_handling: >
      If description is empty, null, or whitespace-only: return category "Other",
      priority "Standard", flag "NEEDS_REVIEW", reason "No classifiable description provided".
      If any required input key is missing: return all fields with flag "NEEDS_REVIEW"
      and reason stating which field was missing. Never raise an exception.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies classify_complaint to each row, and writes the classified results to an output CSV.
    input: >
      input_path (str) — file path to a CSV with columns: complaint_id, date_raised,
      city, ward, location, description, reported_by, days_open.
      output_path (str) — file path where the results CSV will be written.
    output: >
      A CSV file at output_path with columns: complaint_id, category, priority,
      reason, flag. One row per input complaint. The file is written even if
      some rows fail classification.
    error_handling: >
      If a row is malformed or causes an error during classification: skip that row,
      log a warning to stderr with the complaint_id (if available) and error message,
      and continue processing remaining rows. If the input file is missing or unreadable:
      print an error message and exit with a non-zero status code. Never crash silently —
      always produce output for all successfully classified rows.
