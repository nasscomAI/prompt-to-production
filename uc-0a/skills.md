# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classify a single citizen complaint row into a category, priority level,
      reason, and review flag based on the complaint description text.
    input: >
      A single dictionary (dict) representing one CSV row with keys:
      complaint_id (str), date_raised (str), city (str), ward (str),
      location (str), description (str), reported_by (str), days_open (int).
      The description field is the primary input for classification.
    output: >
      A dictionary with exactly these keys:
        - complaint_id (str): echoed from input
        - category (str): exactly one of Pothole, Flooding, Streetlight, Waste,
          Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
        - priority (str): exactly one of Urgent, Standard, Low
        - reason (str): one sentence citing specific words from the description
          that justify the category and priority assignment
        - flag (str): "NEEDS_REVIEW" if the complaint is genuinely ambiguous
          between categories, otherwise empty string ""
    error_handling: >
      If the description field is missing, empty, or null, return category: Other,
      priority: Low, reason: "No description provided", flag: NEEDS_REVIEW.
      If the description does not match any known category, return category: Other
      and flag: NEEDS_REVIEW. Never crash — always return a valid output dict.

  - name: batch_classify
    description: >
      Read an input CSV file of citizen complaints, apply classify_complaint to
      each row, and write all classification results to an output CSV file.
    input: >
      Two string arguments:
        - input_path (str): absolute or relative path to a CSV file (e.g.,
          ../data/city-test-files/test_pune.csv) with columns: complaint_id,
          date_raised, city, ward, location, description, reported_by, days_open
        - output_path (str): path where the results CSV will be written (e.g.,
          results_pune.csv)
    output: >
      A CSV file written to output_path with columns:
        - complaint_id, category, priority, reason, flag
      One row per input complaint. The file must be written even if some rows
      fail classification (partial results are acceptable).
    error_handling: >
      If the input file does not exist or cannot be read, raise a clear error
      message and exit. If individual rows have missing or malformed data, log
      a warning, classify them with category: Other, priority: Low,
      flag: NEEDS_REVIEW, and continue processing remaining rows. Never crash
      mid-batch — always attempt to write partial results. If no rows can be
      processed, write an empty CSV with headers only.
