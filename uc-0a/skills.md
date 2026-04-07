# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag based on description text.
    input: |
      Dictionary containing complaint fields:
      - complaint_id (string)
      - description (string) — the complaint text to classify
      - Other fields from CSV row (for context)
    output: |
      Dictionary containing:
      - category (string) — exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
      - priority (string) — exactly one of: Urgent, Standard, Low
      - reason (string) — one sentence citing specific words from description that justify the classification
      - flag (string) — "NEEDS_REVIEW" if category is genuinely ambiguous, otherwise empty string
    error_handling: |
      - If description is empty or null → category: "Other", flag: "NEEDS_REVIEW", reason: "No description provided"
      - If description contains no recognizable infrastructure keywords → category: "Other", flag: "NEEDS_REVIEW", reason: "Description does not match known complaint categories"
      - If description mentions multiple issues equally → set flag: "NEEDS_REVIEW" and choose the most severe category

  - name: batch_classify
    description: Reads input CSV file, applies classify_complaint to each row, writes output CSV with classification results.
    input: |
      - input_path (string) — path to input CSV file with columns: complaint_id, date_raised, city, ward, location, description, reported_by, days_open
      - output_path (string) — path where results CSV should be written
    output: |
      CSV file written to output_path with columns:
      - complaint_id (string) — copied from input
      - category (string) — classification result
      - priority (string) — classification result
      - reason (string) — justification for classification
      - flag (string) — "NEEDS_REVIEW" or empty
    error_handling: |
      - If input file does not exist → raise FileNotFoundError with clear message
      - If input file has missing required columns → raise ValueError listing which columns are missing
      - If any row fails to classify → log warning but continue processing other rows
      - If output path directory does not exist → create it before writing
      - If output file cannot be written → raise IOError with clear message
