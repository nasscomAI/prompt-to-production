# skills.md — UC-0A

skills:
  - name: classify_complaint
    description: >
      Classifies a single complaint row into the allowed taxonomy,
      assigns priority based on severity keywords, and produces a
      justification quoting the description.
    input: >
      row (dict) with keys complaint_id, date_raised, city, ward, location,
      description, reported_by, days_open. description is required and
      non-empty; other fields may be blank.
    output: >
      dict with keys complaint_id, category, priority, reason, flag.
      category ∈ {Pothole, Flooding, Streetlight, Waste, Noise,
      Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other}.
      priority ∈ {Urgent, Standard, Low}. flag ∈ {NEEDS_REVIEW, ""}.
    error_handling: >
      If description is blank, return category=Other, priority=Standard,
      reason='no description provided', flag=NEEDS_REVIEW. Never crash on
      unexpected columns; ignore them.

  - name: batch_classify
    description: >
      Reads the input CSV, runs classify_complaint on every row, writes
      the results CSV. Prints a per-run summary of Urgent/NEEDS_REVIEW
      counts to stderr.
    input: >
      input_path (str), output_path (str). Input CSV must contain at
      minimum a description column; other columns are echoed as available.
    output: >
      Writes CSV with columns complaint_id, category, priority, reason, flag.
      Returns the list of result dicts.
    error_handling: >
      Skip a row (with a stderr warning) only when its description column
      is missing entirely. Malformed rows do not abort the batch. Never
      silently drop a valid row.
