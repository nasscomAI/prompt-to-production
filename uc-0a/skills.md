skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a category, priority, reason, and optional review flag using a fixed taxonomy and severity keyword rules.
    input:
      type: object
      format: >
        A single complaint record with at least a free-text description field;
        may include an optional complaint_id for traceability.
    output:
      type: object
      format: >
        category (string, one of: Pothole, Flooding, Streetlight, Waste, Noise,
        Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other),
        priority (string, one of: Urgent, Standard, Low),
        reason (string, one sentence citing specific words from the description),
        flag (string, NEEDS_REVIEW if category is genuinely ambiguous, else blank).
    error_handling: >
      If the description is empty or unparseable, output category=Other,
      priority=Low, reason="No parseable description provided", flag=NEEDS_REVIEW.
      If severity keywords (injury, child, school, hospital, ambulance, fire,
      hazard, fell, collapse) are present, priority must be Urgent regardless of
      other signals; never downgrade to Standard or Low.
      If the complaint could legitimately belong to more than one allowed category,
      set flag=NEEDS_REVIEW and choose the most specific matching category.
      Never invent category names outside the allowed list.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes the results to an output CSV with the four classification columns appended.
    input:
      type: file
      format: >
        CSV file path; rows must contain at least a description column;
        category and priority_flag columns are absent (stripped from source data).
    output:
      type: file
      format: >
        CSV file at the specified output path containing all original columns plus
        category, priority, reason, and flag columns produced by classify_complaint
        for every row.
    error_handling: >
      If the input file is missing or unreadable, abort with a clear error message
      and do not create a partial output file.
      If an individual row is malformed or has an empty description, apply the
      classify_complaint error handling for that row (category=Other, priority=Low,
      reason="No parseable description provided", flag=NEEDS_REVIEW) and continue
      processing remaining rows.
      If the input CSV lacks the expected description column, abort with an error
      identifying the missing column.
