# skills.md
skills:
  - name: classify_complaint
    description: Classifies a single complaint row into a schema containing category, priority, reason, and an optional review flag.
    input: Dictionary representing a single complaint record.
    output: Dictionary with keys `complaint_id`, `category`, `priority`, `reason`, and `flag`.
    error_handling: If inputs are invalid or completely ambiguous, output category `Other` and set flag to `NEEDS_REVIEW`.

  - name: batch_classify
    description: Reads an input CSV, classifies each row individually using classify_complaint, and writes to an output CSV.
    input: String file paths for input and output CSVs.
    output: Writes parsed CSV results to the output path.
    error_handling: Skips completely malformed rows with logging, preventing a full program crash, and outputs results even if some rows fail.
