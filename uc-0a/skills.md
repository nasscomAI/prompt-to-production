# skills.md - UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint row into a fixed category, assigns a
      priority level, generates a justification reason, and sets a review flag when
      the complaint is ambiguous.
    input: >
      A Python dict representing one CSV row with at least a description key
      (string) and a complaint_id key (string or int).
    output: >
      A Python dict with exactly four keys:
        - category  (str) - one of: Pothole, Flooding, Streetlight, Waste, Noise,
                            Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
        - priority  (str) - one of: Urgent, Standard, Low
        - reason    (str) - one sentence citing specific words from the description
        - flag      (str) - NEEDS_REVIEW if ambiguous, otherwise empty string
    error_handling: >
      If the description field is missing or empty, return category: Other,
      priority: Low, reason: No description provided, flag: NEEDS_REVIEW.
      Never raise an unhandled exception - always return a valid output dict.

  - name: batch_classify
    description: >
      Reads an input CSV of complaint rows, applies classify_complaint to each row,
      and writes a results CSV with the original complaint_id plus the four
      classification fields.
    input: >
      Two strings: input_path (path to the source CSV file containing at least
      complaint_id and description columns) and output_path (path where the results
      CSV will be written).
    output: >
      A CSV file written to output_path with columns: complaint_id, category,
      priority, reason, flag. One row per input row. Returns the count of rows
      successfully classified as an int.
    error_handling: >
      If a row fails classification, write category: Other, priority: Low,
      reason: Classification error, flag: NEEDS_REVIEW for that row and continue
      processing remaining rows. If the input file cannot be read, raise a
      FileNotFoundError with a descriptive message. Never silently skip rows.
