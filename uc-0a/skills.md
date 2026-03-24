# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint row into a structured output with
      category, priority, reason, and flag fields using the R.I.C.E enforcement rules.
    input: >
      A single dictionary (row) with keys: complaint_id, date_raised, city, ward,
      location, description, reported_by, days_open.
      The `description` field is the primary text used for classification.
    output: >
      A dictionary with keys:
        - complaint_id (str): Echoed from input.
        - category (str): Exactly one of — Pothole, Flooding, Streetlight, Waste,
          Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
        - priority (str): One of — Urgent, Standard, Low.
        - reason (str): One sentence citing specific words from the description.
        - flag (str): "NEEDS_REVIEW" if category is ambiguous, otherwise empty string.
    error_handling: >
      If `description` is missing, empty, or null: return category "Other",
      priority "Low", flag "NEEDS_REVIEW", reason "Description is missing or empty."
      If `description` does not clearly map to any single category: return
      category "Other", flag "NEEDS_REVIEW", with reason explaining the ambiguity.
      Never crash — always return a valid output dict for every input row.

  - name: batch_classify
    description: >
      Reads an input CSV file of citizen complaints, applies classify_complaint
      to each row, and writes the classified results to an output CSV file.
    input: >
      Two file paths:
        - input_path (str): Path to the input CSV file (e.g., test_pune.csv) containing
          columns: complaint_id, date_raised, city, ward, location, description,
          reported_by, days_open.
        - output_path (str): Path to write the results CSV file (e.g., results_pune.csv).
    output: >
      A CSV file written to output_path with columns:
        - complaint_id, category, priority, reason, flag.
      One row per input complaint. Row count in output must equal row count in input.
    error_handling: >
      If the input file does not exist or cannot be read: print a clear error
      message and exit gracefully without crashing.
      If an individual row fails classification: write a row with category "Other",
      priority "Low", flag "NEEDS_REVIEW", reason "Classification failed for this row."
      Never skip rows — every input row must produce an output row.
      Never crash on malformed rows — handle them gracefully and continue processing.
