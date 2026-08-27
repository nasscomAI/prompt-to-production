# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint row into a category, priority level,
      and reason, and sets a review flag when the category is ambiguous.
    input: >
      A dict representing one CSV row. Must contain a non-empty string field
      `description`. All other fields (e.g. complaint_id) are passed through
      unchanged and must not influence classification logic.
    output: >
      A dict with exactly five fields:
        - complaint_id: passed through from input
        - category: one of — Pothole, Flooding, Streetlight, Waste, Noise,
          Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
          (exact string, no variations)
        - priority: one of — Urgent, Standard, Low
          (Urgent if description contains any severity keyword:
          injury, child, school, hospital, ambulance, fire, hazard, fell, collapse)
        - reason: one sentence citing specific words from the description
          that justify the chosen category and priority
        - flag: "NEEDS_REVIEW" if category is Other due to ambiguity, else blank string
    error_handling: >
      If `description` is missing, null, or empty: set category to Other,
      priority to Low, reason to "Description was empty or missing — cannot classify.",
      and flag to NEEDS_REVIEW. Do not raise an exception; return a valid output dict.

  - name: batch_classify
    description: >
      Reads an input CSV of complaint rows, applies classify_complaint to each row,
      and writes the results to an output CSV — continuing past row-level errors
      without crashing.
    input: >
      Two file paths as strings:
        - input_path: path to a CSV file with at least a `description` column
        - output_path: path where the results CSV will be written
      The input CSV may contain extra columns; they are ignored.
    output: >
      A CSV file at output_path containing one row per input row with columns:
      complaint_id, category, priority, reason, flag.
      Rows that raised an exception during classify_complaint are written with
      category: Other, priority: Low, reason: describing the error, flag: NEEDS_REVIEW.
    error_handling: >
      If input_path does not exist or cannot be read: raise FileNotFoundError with
      a descriptive message and do not create an output file.
      If an individual row fails during classification: catch the exception, write
      a NEEDS_REVIEW fallback row for that complaint_id, and continue processing
      remaining rows. Log each row-level failure to stderr.
