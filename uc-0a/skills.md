# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a structured output with category, priority, reason, and review flag.
    input: >
      A single row (dict/object) containing at minimum a complaint description field (string).
      Example: { "description": "Large pothole near school on MG Road causing traffic issues" }
    output: >
      A dict/object with exactly four fields:
        - category (string): One of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
        - priority (string): One of Urgent, Standard, Low
        - reason (string): One sentence citing specific words from the description
        - flag (string): "NEEDS_REVIEW" if ambiguous, otherwise empty string
      Example: { "category": "Pothole", "priority": "Urgent", "reason": "Description mentions 'pothole' near 'school', triggering Urgent priority.", "flag": "" }
    error_handling: >
      If the description is empty or unintelligible, set category to "Other", priority to "Low",
      reason to "Description is empty or unintelligible", and flag to "NEEDS_REVIEW".
      If the description is ambiguous across multiple categories, pick the best match,
      and set flag to "NEEDS_REVIEW". Never leave any of the four output fields missing.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row, and writes the results to an output CSV file.
    input: >
      Two file paths:
        - input_path (string): Path to the input CSV containing complaint rows with a description column.
        - output_path (string): Path where the classified output CSV will be written.
    output: >
      A CSV file at output_path containing all original columns plus four new columns:
      category, priority, reason, flag. Each row is the result of classify_complaint
      applied to that row's description. The file is written with UTF-8 encoding.
    error_handling: >
      If the input file does not exist or is not a valid CSV, raise a clear error message
      and exit without writing any output. If an individual row fails classification
      (e.g., missing description column), set that row's output to category="Other",
      priority="Low", reason="Classification failed — missing description", flag="NEEDS_REVIEW",
      and continue processing remaining rows.
