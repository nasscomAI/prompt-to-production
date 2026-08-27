skills:
  - name: classify_complaint
    description: Classifies a single complaint row based on RICE enforcement rules for category, priority, reason, and flags.
    input: Dictionary containing a complaint row with fields like description, date_raised, city, ward, etc.
    output: Dictionary with standardized keys complaint_id, category, priority, reason, and flag.
    error_handling: Handles genuine ambiguity by marking "Other" and adding "NEEDS_REVIEW", gracefully processes missing fields.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint per row, and writes out the formatted results CSV.
    input: String path for input CSV and string path for output CSV.
    output: Writes a CSV file directly to the given output path.
    error_handling: Flags nulls, catches unexpected row failures independently to write placeholder empty/flagged output rows, and ensures the script finishes processing all valid rows.
