# skills.md


skills:
  - name: classify_complaint
    description: Categorizes a single citizen complaint and assigns priority based on severity keywords.
    input: String (the complaint description text).
    output: Dictionary/JSON containing category, priority, reason, and flag.
    error_handling: If the category is ambiguous or cannot be determined, set category to "Other" and flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Processes an entire CSV file of complaints, applying classify_complaint to each row and saving results to a new CSV.
    input: Path to the input CSV file.
    output: Path to the generated output CSV file.
    error_handling: Handles missing files or invalid CSV formats by logging errors and skipping corrupted rows.
