# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row based on its text description into its category and priority.
    input: dict representing a single complaint record, containing at least the `description` and `complaint_id` fields.
    output: dict with classification fields: `category`, `priority`, `reason`, and `flag`.
    error_handling: For null descriptions or unclassifiable text, returns `category: 'Other'` and `flag: 'NEEDS_REVIEW'`.

  - name: batch_classify
    description: Processes a whole input CSV of citizen complaints, applying the classification skill per row, and writes it to an output CSV.
    input: file paths for input CSV (e.g., `test_pune.csv`) and output CSV (e.g., `results_pune.csv`).
    output: None (Writes the resulting CSV with additional classification columns).
    error_handling: Handles missing input files or malformed CSV rows gracefully; ensures output is produced even if individual rows fail.
