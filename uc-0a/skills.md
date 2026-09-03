skills:
  - name: classify_complaint
    description: >
      Classifies a single complaint row and returns exactly four classification
      fields — category, priority, reason, flag — with no complaint_id in the
      output of this single-row skill.
    input: >
      A single complaint record dict with the row structure: complaint_id (str),
      date_raised (str, YYYY-MM-DD), city (str), ward (str), location (str),
      description (str, the free-text complaint), reported_by (str), days_open (int).
      Only the description field drives classification; location/city/ward may be
      read where they legitimately clarify category. The category and priority
      input fields, if present, are ignored.
    output: >
      A dict with exactly four keys: category (one of Pothole, Flooding,
      Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard,
      Drain Blockage, Other), priority (one of Urgent, Standard, Low), reason
      (one sentence citing specific words from the description that justify the
      category and priority), and flag (NEEDS_REVIEW or blank).
    error_handling: >
      If description is empty, blank, or unusable, return category Other,
      priority Standard, reason stating the description was insufficient to
      classify, and flag NEEDS_REVIEW. If the category is ambiguous, apply this
      ordered check: (1) if a supporting token for one allowed category is
      traceable to the row's own words (description, or location/city/ward where
      legitimately relevant), assign that allowed category but still set flag
      NEEDS_REVIEW; (2) otherwise return category Other with flag NEEDS_REVIEW.
      Never invent a category, sub-category, severity keyword, or fact. Always
      honour the mandatory severity-keyword rule (injury, child, school,
      hospital, ambulance, fire, hazard, fell, collapse imply priority Urgent),
      regardless of the flag or category chosen.
  - name: batch_classify
    description: >
      Reads a complaint CSV, applies classify_complaint to every row, preserves
      each row's complaint_id for traceability, and writes a results CSV. The
      batch CSV output therefore contains complaint_id plus the four
      classification fields — complaint_id, category, priority, reason, flag —
      unlike the single-row skill output which has only the four fields.
    input: >
      input_path (str) pointing to a CSV with the header
      complaint_id,date_raised,city,ward,location,description,reported_by,days_open
      and exactly one row per complaint, and output_path (str) where the results
      CSV will be written.
    output: >
      A CSV file written at output_path containing one row per input complaint
      with the fields: complaint_id (carried through), category, priority,
      reason, flag. Every input row produces a corresponding output row; no rows
      are silently dropped.
    error_handling: >
      If the file is missing, unreadable, has an empty description, or a
      malformed/invalid row, do not fail the whole batch or silently skip rows:
      write a best-effort row for the affected complaint using category Other,
      priority Standard, a reason noting the issue, and flag NEEDS_REVIEW, and
      continue processing remaining rows. If the file itself cannot be parsed at
      all, surface the error rather than writing an empty or fabricated results
      file. Classification failures within a row never block the rest of the
      batch.
