skills:
  - name: classify_complaint
    description: Classify one citizen complaint row into a fixed category, priority, reason, and review flag.
    input: >
      A dict representing one CSV row. Expected keys include complaint_id
      and description; other civic fields may be present but are not required
      for classification.
    output: >
      A dict with keys complaint_id, category, priority, reason, flag.
      category is one allowed taxonomy string; priority is Urgent, Standard,
      or Low; reason is one sentence; flag is NEEDS_REVIEW or "".
    error_handling: >
      Missing or blank description → category Other, priority Standard,
      flag NEEDS_REVIEW, reason states description is missing.
      Non-dict or unreadable row → same shape with complaint_id "UNKNOWN"
      if id is absent. Never raise to the caller.

  - name: batch_classify
    description: Read a complaints CSV, classify every row, and write results CSV without stopping on bad rows.
    input: >
      input_path (str) to test_[city].csv and output_path (str) for
      results_[city].csv. Input delimiter is comma; header row required.
    output: >
      A CSV at output_path with header
      complaint_id,category,priority,reason,flag and one row per input row.
      Returns nothing; writes the file even if some rows fail.
    error_handling: >
      Unreadable file → raise after writing nothing only if the file cannot
      be opened. Per-row parse/classify errors are caught, emitted as
      Other + NEEDS_REVIEW, and processing continues. Null/empty description
      is not a crash; it is flagged.
