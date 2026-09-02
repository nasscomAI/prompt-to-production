# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify a single complaint row into a controlled category, a priority level, a cited reason, and an optional review flag.
    input: >
      A dict for one CSV row. Required key: description (str). Optional keys used
      for disambiguation: complaint_id, location, ward. Other columns are ignored.
    output: >
      A dict with exactly these keys:
      complaint_id (str, echoed from input or "" if absent),
      category (str, one of the 10 allowed values),
      priority (str, one of Urgent | Standard | Low),
      reason (str, one sentence citing specific word(s) from the description),
      flag (str, "NEEDS_REVIEW" or "").
    error_handling: >
      If description is missing, empty, or not text, return category "Other",
      priority "Low", flag "NEEDS_REVIEW", and a reason noting the description
      was unreadable. Severity terms are matched as substrings of a word so
      variants like hospitalised, collapsed, and children still force Urgent,
      even when the category is Other. When no severity term is present, a valid
      complaint is Standard and Low is reserved for empty or non-actionable
      descriptions. If no allowed category clearly matches, return category
      "Other" with flag "NEEDS_REVIEW" rather than guessing.

  - name: batch_classify
    description: Read an input CSV, apply classify_complaint to every row, and write the results CSV with the five output fields.
    input: >
      input_path (str) to a CSV containing at least complaint_id and description
      columns; output_path (str) for the results CSV to be written.
    output: >
      Writes a CSV with header complaint_id,category,priority,reason,flag and one
      row per input row. Returns None. Prints a short completion summary.
    error_handling: >
      Never aborts the whole run because of one bad row: any row that raises is
      written with category "Other", priority "Low", flag "NEEDS_REVIEW", and a
      reason describing the failure. Missing input file raises a clear error
      before processing. Output is always produced when the input is readable,
      even if some individual rows failed.
