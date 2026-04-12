# skills.md
skills:
  - name: classify_complaint
    description: Evaluates a single complaint row to determine the category, priority, reason, and flag based on predefined taxonomy.
    input: Dictionary representing a single complaint row, primarily reading the 'description' field.
    output: Dictionary with keys 'category', 'priority', 'reason', and 'flag'.
    error_handling: Unresolvable or ambiguous descriptions return category 'Other' with flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint per row sequentially, and writes to an output CSV.
    input: input_path (string) representing source CSV location, output_path (string) representing destination CSV location.
    output: Writes results out to the destination CSV file.
    error_handling: Handles missing data gracefully, flags nulls or empty descriptions with 'NEEDS_REVIEW', and ensures a valid output CSV is written even if some rows are problematic.
