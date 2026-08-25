# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row into a category, priority, reason, and flag.
    input: >
      A single CSV row as a dict containing at minimum `complaint_id` (string)
      and `description` (free-text string from the citizen).
    output: >
      A dict with exactly five keys:
        - `complaint_id`: preserved from input, unchanged.
        - `category`: exactly one of Pothole, Flooding, Streetlight, Waste, Noise,
          Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
        - `priority`: exactly one of Urgent, Standard, Low.
          Must be Urgent if the description contains any severity keyword
          (case-insensitive): injury, child, school, hospital, ambulance, fire,
          hazard, fell, collapse.
        - `reason`: one sentence citing specific words from the description that
          justify the chosen category and priority.
        - `flag`: "NEEDS_REVIEW" if the category cannot be confidently determined
          from the description alone; blank string otherwise.
    error_handling: >
      If the description is missing, empty, or not a string, return category "Other",
      priority "Low", reason citing the missing data, and flag "NEEDS_REVIEW".
      Never drop the row or raise an unhandled exception.

  - name: batch_classify
    description: Read an input CSV, apply classify_complaint to each row, and write the results to an output CSV.
    input: >
      Two file paths: `input_path` (path to a CSV file with at least `complaint_id`
      and `description` columns) and `output_path` (path where the results CSV
      will be written).
    output: >
      A CSV file written to `output_path` with columns: complaint_id, category,
      priority, reason, flag. One output row per input row — no rows dropped or
      duplicated. The file must be a valid CSV readable by any standard parser.
    error_handling: >
      If a row fails classification (malformed data, missing fields), write the row
      to the output with category "Other", priority "Low", reason describing the
      error, and flag "NEEDS_REVIEW". Never crash the batch — always produce output
      even if some rows fail. Log a warning for each failed row to stderr.
