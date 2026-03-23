# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag using the UC-0A fixed taxonomy and severity rules.
    input: >
      One row as dict-like object with at least complaint_id (string/int) and complaint description text field
      (if multiple text fields exist, use the primary complaint description column from input CSV).
    output: >
      Dict with keys: complaint_id, category, priority, reason, flag.
      category must be one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage,
      Heritage Damage, Heat Hazard, Drain Blockage, Other.
      priority must be one of: Urgent, Standard, Low.
      flag is NEEDS_REVIEW or empty string.
    error_handling: >
      If complaint text is missing/blank, return category=Other, priority=Standard,
      reason="Missing complaint description; unable to classify confidently.", flag=NEEDS_REVIEW.
      If text is ambiguous across categories, return best-safe category=Other with flag=NEEDS_REVIEW.
      Never throw for bad row shape; always return a valid output dict.

  - name: batch_classify
    description: Reads an input complaint CSV, applies classify_complaint per row, and writes a results CSV with stable schema.
    input: >
      input_path (string path to test_[city].csv) and output_path (string path for results CSV).
      Input contains complaint rows where category/priority columns are absent.
    output: >
      CSV file at output_path with columns: complaint_id, category, priority, reason, flag.
      Writes one output row per input row in original order.
    error_handling: >
      Handle malformed rows defensively: produce a fallback row with category=Other,
      priority=Standard, explanatory reason, and flag=NEEDS_REVIEW.
      Continue processing remaining rows even if some rows fail parsing.
      If file read/write errors occur, raise a clear exception with file path context.
