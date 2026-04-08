skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a category, assigns priority, generates a reason citing words from the description, and sets a review flag if ambiguous.
    input: >
      A dictionary containing at minimum the field 'description' (string) — the raw
      citizen complaint text. Optional fields: complaint_id (string), city (string),
      ward (string), location (string).
    output: >
      A dictionary with keys:
        complaint_id (string): copied from input or empty string if missing.
        category (string): exactly one of — Pothole, Flooding, Streetlight, Waste,
          Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
        priority (string): exactly one of — Urgent, Standard, Low.
        reason (string): one sentence citing specific words from the description.
        flag (string): NEEDS_REVIEW if ambiguous, else empty string.
    error_handling: >
      If description is empty or None, return category=Other, priority=Low,
      reason='No description provided — cannot classify.', flag=NEEDS_REVIEW.
      If the LLM returns an invalid category not in the allowed list, override it
      with Other and set flag=NEEDS_REVIEW. Never raise an exception — always
      return a valid dictionary even on failure.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes a results CSV with the classification output appended.
    input: >
      Two strings:
        input_path (string): absolute or relative path to a CSV file with columns
          including at minimum 'complaint_id' and 'description'.
        output_path (string): path where the output CSV should be written.
    output: >
      A CSV file written to output_path with columns:
        complaint_id, category, priority, reason, flag.
      One row per input complaint. Function returns the count of successfully
      classified rows as an integer.
    error_handling: >
      If a row is malformed or missing required fields, write a row with
      category=Other, priority=Low, reason='Row error — skipped.', flag=NEEDS_REVIEW
      and continue processing. Never crash on a single bad row. If the input file
      does not exist, raise FileNotFoundError with a clear message. If the output
      directory does not exist, create it. Log the count of error rows at completion.
