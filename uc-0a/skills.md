# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classify a single citizen complaint row into category, priority, reason,
      and flag using the fixed UC-0A taxonomy and severity rules.
    input:
      type: dict
      format: >
        One complaint row with keys: complaint_id, date_raised, city, ward,
        location, description, reported_by, days_open. The description field
        is the primary classification signal.
      required_keys:
        - complaint_id
        - description
    output:
      type: dict
      format: >
        Dict with keys: complaint_id, category, priority, reason, flag.
      fields:
        complaint_id: "Copied from input row."
        category: "Exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
        priority: "Exactly one of: Urgent, Standard, Low."
        reason: "One sentence citing specific words from the description."
        flag: "NEEDS_REVIEW if category is ambiguous; otherwise blank string."
    rules:
      - "Use description as primary signal; location and ward only as tie-breakers."
      - "Set priority to Urgent if any severity keyword appears: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
      - "If two categories are equally plausible, return category: Other and flag: NEEDS_REVIEW."
      - "Never invent sub-categories or synonyms."
    error_handling:
      missing_description: >
        Return category: Other, priority: Standard, reason citing that
        description is missing or empty, flag: NEEDS_REVIEW.
      missing_complaint_id: >
        Return classification with complaint_id set to empty string;
        include flag: NEEDS_REVIEW and reason noting missing complaint_id.
      ambiguous_category: >
        Return category: Other, flag: NEEDS_REVIEW, and reason explaining
        which categories are equally plausible.
      invalid_input: >
        Do not crash. Return a result dict with flag: NEEDS_REVIEW and a
        reason describing the input problem.

  - name: batch_classify
    description: >
      Read an input CSV of complaint rows, apply classify_complaint to every
      row, and write the classified results to an output CSV.
    input:
      type: file paths
      format: >
        input_path: path to test_[city].csv (e.g. ../data/city-test-files/test_pune.csv).
        output_path: path to write results CSV (e.g. results_pune.csv).
      input_csv_columns:
        - complaint_id
        - date_raised
        - city
        - ward
        - location
        - description
        - reported_by
        - days_open
    output:
      type: CSV file
      format: >
        CSV with columns: complaint_id, category, priority, reason, flag.
        One output row per input row, in the same order as input.
    behaviour:
      - "Read all rows from input_path using csv.DictReader."
      - "Call classify_complaint on each row."
      - "Write all results to output_path using csv.DictWriter."
      - "Produce output even if some rows fail classification."
    error_handling:
      missing_input_file: >
        Raise a clear FileNotFoundError with the input path; do not write
        a partial output file.
      bad_row: >
        Catch per-row failures without stopping the batch. Write a result
        row with flag: NEEDS_REVIEW and a reason describing the failure.
        Continue processing remaining rows.
      empty_input: >
        Write an output CSV with headers only (complaint_id, category,
        priority, reason, flag) and zero data rows.
      null_or_empty_fields: >
        Pass the row to classify_complaint; let it handle missing
        description or complaint_id per its error_handling rules.
