# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classify a single citizen-complaint row into a category, priority level,
      human-readable reason, and an optional ambiguity flag.
    input: >
      A dictionary (CSV row) with at minimum the keys: complaint_id, description.
      Other columns (date_raised, city, ward, location, reported_by, days_open)
      may be present but are not used for classification.
    output: >
      A dictionary with exactly these keys:
        - complaint_id  (str)  — passed through from the input row.
        - category      (str)  — one of: Pothole, Flooding, Streetlight, Waste,
                                  Noise, Road Damage, Heritage Damage,
                                  Heat Hazard, Drain Blockage, Other.
        - priority      (str)  — one of: Urgent, Standard, Low.
        - reason        (str)  — one sentence citing specific words from the
                                  description that justify the category and
                                  priority choice.
        - flag          (str)  — "NEEDS_REVIEW" if the category is genuinely
                                  ambiguous; otherwise blank ("").
    error_handling: >
      - If the description is missing, empty, or null: set category to "Other",
        priority to "Low", reason to "No description provided", and flag to
        "NEEDS_REVIEW".
      - If the description matches two or more categories with roughly equal
        confidence: choose the single best-fit category, set flag to
        "NEEDS_REVIEW", and explain the ambiguity in the reason field.
      - If a severity keyword (injury, child, school, hospital, ambulance, fire,
        hazard, fell, collapse) is present but the category is unclear: still
        set priority to "Urgent" and flag to "NEEDS_REVIEW".
      - Category strings must be returned exactly as listed — no abbreviations,
        plurals, or synonyms.

  - name: batch_classify
    description: >
      Read an input CSV of citizen complaints, apply classify_complaint to every
      row, and write the classified results to an output CSV.
    input: >
      Two file-path strings:
        - input_path   — path to a CSV with columns: complaint_id, date_raised,
                          city, ward, location, description, reported_by,
                          days_open (category and priority_flag are stripped).
        - output_path  — path where the results CSV will be written.
    output: >
      A CSV file at output_path with columns:
        complaint_id, category, priority, reason, flag.
      One row per input complaint. Column order and header names must match
      exactly.
    error_handling: >
      - If a row fails classification (e.g., malformed data), write the row to
        the output with category "Other", priority "Low",
        reason "Classification failed — malformed input row", and
        flag "NEEDS_REVIEW". Never skip a row silently.
      - If the input file is empty (header only), write an output file with just
        the header row.
      - If the input file does not exist or cannot be read, raise a
        FileNotFoundError with a descriptive message.
      - Log a warning to stderr for every row that triggers error handling,
        including the complaint_id if available.
