# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into category, priority, reason, and flag according to the fixed taxonomy and severity-keyword rules.
    input: >
      A single complaint record as a dict with at least one key:
        - description (string) — the raw complaint text to classify
      All other columns (complaint_id, city, date, etc.) are passed through unchanged
      and must NOT influence classification.
    output: >
      A dict with four fields added to the input record:
        - category (string) — exactly one of: Pothole · Flooding · Streetlight · Waste ·
          Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other
        - priority (string) — exactly one of: Urgent · Standard · Low
          (Urgent if description contains any of: injury, child, school, hospital,
          ambulance, fire, hazard, fell, collapse — case-insensitive)
        - reason (string) — one sentence citing specific words from the description
        - flag (string) — "NEEDS_REVIEW" if category is genuinely ambiguous, else ""
    error_handling: >
      If description is empty or None: output category "Other", priority "Low",
      reason "No description provided", flag "NEEDS_REVIEW".
      If the description exists but category cannot be determined: output category "Other",
      flag "NEEDS_REVIEW" — never guess a category to avoid the flag.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes a results CSV with all original columns plus the four classification fields.
    input: >
      Two file paths as strings:
        - input_path — path to the source CSV (e.g. test_pune.csv); must contain a
          "description" column; other columns are passed through unchanged
        - output_path — path to write the results CSV (e.g. results_pune.csv)
    output: >
      A CSV file written to output_path containing all original columns plus:
        category · priority · reason · flag
      One row per input row, in original order. Also prints a summary to stdout:
        total rows processed · Urgent count · NEEDS_REVIEW count
    error_handling: >
      If input_path does not exist: raise FileNotFoundError with the full path.
      If the "description" column is missing: raise ValueError naming the missing column.
      If a single row fails classification: write category "Other", flag "NEEDS_REVIEW",
      reason "Classification error: [exception message]" for that row and continue —
      do not abort the entire batch.
