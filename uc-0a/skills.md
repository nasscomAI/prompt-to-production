skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint row into a category, priority level,
      reason, and optional review flag by applying the RICE enforcement rules
      defined in agents.md.
    input: >
      A dict representing one CSV row with at least the key `description`
      (string) — the raw citizen complaint text. The `complaint_id` field is
      passed through unchanged if present.
    output: >
      A dict with exactly four classification fields:
        - category  (string): exactly one of — Pothole, Flooding, Streetlight,
          Waste, Noise, Road Damage, Heritage Damage, Heat Hazard,
          Drain Blockage, Other
        - priority  (string): exactly one of — Urgent, Standard, Low.
          Must be Urgent if the description contains any severity keyword:
          injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.
        - reason    (string): one sentence citing specific words from the
          complaint description that justify the category and priority chosen.
        - flag      (string): "NEEDS_REVIEW" if the category is genuinely
          ambiguous; blank string ("") otherwise.
    error_handling: >
      - If `description` is missing, empty, or None: set category to "Other",
        priority to "Low", reason to "Description field is missing or empty.",
        and flag to "NEEDS_REVIEW".
      - If the description does not clearly match any of the 9 named categories:
        set category to "Other" and flag to "NEEDS_REVIEW"; do not guess.
      - Never output a category string that is not in the allowed list; if in
        doubt, fall back to "Other + NEEDS_REVIEW".

  - name: batch_classify
    description: >
      Reads an input CSV of citizen complaints, applies classify_complaint to
      every row, and writes a results CSV. Continues processing remaining rows
      even if individual rows fail.
    input: >
      Two file-path strings:
        - input_path  (str): path to test_[city].csv — must contain at minimum
          a `description` column; `complaint_id` column is passed through if
          present.
        - output_path (str): path where the results CSV will be written.
    output: >
      A CSV file at output_path containing one row per input complaint with
      columns: complaint_id (if present in input), description, category,
      priority, reason, flag.
      All values conform to the constraints enforced by classify_complaint.
    error_handling: >
      - If a row is malformed or `description` is absent: call classify_complaint
        with an empty description so that row receives "Other / Low / NEEDS_REVIEW"
        and processing continues.
      - If the input file does not exist or cannot be parsed: raise a clear
        FileNotFoundError / ValueError with the path in the message; do not
        produce a partial output file.
      - Log (print to stderr) the complaint_id and error reason for every row
        that falls back to NEEDS_REVIEW due to a processing error.
