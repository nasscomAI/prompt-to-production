# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Given a single complaint row dict, returns a dict with complaint_id, category,
      priority, reason, and flag, following the classification schema in README.md.
    input: >
      dict with keys: complaint_id (str), date_raised (str), city (str), ward (str),
      location (str), description (str), reported_by (str), days_open (str)
    output: >
      dict with keys: complaint_id (str), category (str — one of the 10 allowed values),
      priority (str — Urgent|Standard|Low), reason (str — one sentence citing description
      words), flag (str — NEEDS_REVIEW or empty)
    error_handling: >
      If description is empty or missing, set category=Other, priority=Low,
      reason="No description provided.", flag=NEEDS_REVIEW. Never raise an exception.

  - name: batch_classify
    description: >
      Reads an input CSV of complaints, applies classify_complaint to each row, and
      writes a results CSV with complaint_id, category, priority, reason, flag.
    input: >
      input_path (str — path to CSV with columns: complaint_id, date_raised, city, ward,
      location, description, reported_by, days_open)
    output: >
      output_path (str — path to write results CSV with columns: complaint_id, category,
      priority, reason, flag)
    error_handling: >
      Skip rows that fail to parse (log a warning). Flush partial results on any row
      failure. Always produce output even if some rows error. Null or blank descriptions
      produce category=Other, priority=Low, flag=NEEDS_REVIEW.
