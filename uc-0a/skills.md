# skills.md

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row into category, priority, reason, and flag fields.
    input: A dict with keys: complaint_id (string/int), complaint_description (string).
    output: A dict with keys: complaint_id, category, priority, reason, flag. Category is one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. Priority is one of: Urgent, Standard, Low. Reason is one sentence citing specific words from the description. Flag is NEEDS_REVIEW or blank.
    error_handling: If the category cannot be determined from the description alone, output category: Other and flag: NEEDS_REVIEW. If the input row is missing or description is empty, return category: Other, priority: Standard, reason: "No description provided", and flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Read an input CSV of complaints, apply classify_complaint per row, and write results to an output CSV.
    input: Two file paths — input_path (path to test_[city].csv) and output_path (path to write results_[city].csv). The input CSV has columns including complaint_id and complaint_description; category and priority_flag columns are stripped.
    output: A CSV file at output_path with columns: complaint_id, category, priority, reason, flag.
    error_handling: Flag null or malformed rows instead of crashing. Produce output even if some rows fail — mark failed rows with category: Other, priority: Standard, reason: "Row could not be processed", flag: NEEDS_REVIEW.
