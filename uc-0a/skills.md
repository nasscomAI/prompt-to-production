skills:
  - name: classify_complaint
    description: Classify one citizen complaint into category, priority, reason, and review flag using only the fields of that row.
    input: >
      dict with keys: complaint_id (str), date_raised (str), city (str), ward (str),
      location (str), description (str), reported_by (str), days_open (str|int).
      `description` is the primary evidence field.
    output: >
      dict with keys: complaint_id (str, echoed from input),
      category (str, one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage,
      Heritage Damage, Heat Hazard, Drain Blockage, Other),
      priority (str, one of: Urgent, Standard, Low),
      reason (str, one sentence citing tokens from description),
      flag (str, either "NEEDS_REVIEW" or "").
    error_handling: >
      Missing/empty description → category=Other, priority=Standard, flag=NEEDS_REVIEW,
      reason states "description missing or empty". Description present but ambiguous
      between two categories → pick the more specific one, flag=NEEDS_REVIEW. Severity
      keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse)
      present → priority=Urgent regardless of other signals. Never raise; always return
      a complete dict.

  - name: batch_classify
    description: Read an input CSV of complaints, apply classify_complaint to each row, write a results CSV.
    input: >
      input_path (str, path to CSV with header: complaint_id,date_raised,city,ward,
      location,description,reported_by,days_open),
      output_path (str, path to write results CSV).
    output: >
      Writes CSV with header: complaint_id,category,priority,reason,flag.
      One output row per input row (including failed rows). Returns None.
    error_handling: >
      Malformed row (missing columns, unparseable) → emit a result row with
      category=Other, priority=Standard, flag=NEEDS_REVIEW, and a reason describing
      the parse failure. Missing input file → raise FileNotFoundError before opening
      the output file (do not create an empty output). Row-level failures must not
      abort the batch; the output file must contain exactly len(input_rows) result rows.
