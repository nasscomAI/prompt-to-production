# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint row into a category, priority level,
      reason, and ambiguity flag based solely on the complaint description text.
    input: >
      A dictionary representing one CSV row with keys: complaint_id, date_raised,
      city, ward, location, description, reported_by, days_open.
      Only 'complaint_id' and 'description' are used for classification.
    output: >
      A dictionary with keys:
        - complaint_id (str): echoed from input
        - category (str): exactly one of Pothole, Flooding, Streetlight, Waste,
          Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
        - priority (str): exactly one of Urgent, Standard, Low
        - reason (str): one sentence citing specific words from description
        - flag (str): "NEEDS_REVIEW" if ambiguous or Other, else empty string
    error_handling: >
      If description is empty, null, or missing: return category=Other,
      priority=Low, flag=NEEDS_REVIEW, reason="Empty or missing description."
      Never raise an exception — always return a valid classification dict.

  - name: batch_classify
    description: >
      Reads an input CSV file, applies classify_complaint to each row, and writes
      the classification results to an output CSV file.
    input: >
      Two file paths as strings:
        - input_path: path to the source CSV (test_[city].csv)
        - output_path: path to write the results CSV
    output: >
      A CSV file at output_path with columns: complaint_id, category, priority,
      reason, flag. One row per input complaint. Also prints a summary to stdout
      showing total rows processed, count per category, and count of Urgent rows.
    error_handling: >
      If a row fails classification, write it to output with category=Other,
      flag=NEEDS_REVIEW, reason="Classification failed for this row."
      Never crash the batch — continue processing remaining rows.
      If the input file is missing or unreadable, print an error and exit with
      a non-zero status code.
