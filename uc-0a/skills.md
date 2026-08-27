# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag fields according to the UC-0A schema.
    input: A single complaint record — one string field named `description` containing the raw citizen-submitted text.
    output: >
      A structured record with four fields:
        - category (str): exactly one of Pothole · Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other
        - priority (str): Urgent · Standard · Low
        - reason (str): one sentence citing specific words from the description
        - flag (str): NEEDS_REVIEW or blank
    error_handling: >
      If the description is empty or unparseable, output category: Other, priority: Low,
      reason: "Description too ambiguous to classify.", flag: NEEDS_REVIEW.
      If a severity keyword is present but category is unclear, still set priority: Urgent
      and flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes a results CSV with the four classification fields appended.
    input: >
      A CSV file path (str) with at minimum a `description` column. The `category`
      and `priority_flag` columns are stripped from the input — do not expect them.
      CLI usage: --input <path> --output <path>
    output: >
      A CSV file written to the specified output path containing all original columns
      plus four new columns: category, priority, reason, flag. One row per input row,
      no rows dropped.
    error_handling: >
      If the input file is missing or the `description` column is absent, exit with a
      clear error message and do not write a partial output file. If an individual row
      fails classification, write category: Other, priority: Low, flag: NEEDS_REVIEW,
      and log the row index to stderr — do not halt the batch.
