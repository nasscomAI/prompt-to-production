# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint description into category, priority, reason, and flag fields according to the enforcement schema.
    input: "String containing complaint description text"
    output: "JSON object with keys: category (string), priority (string), reason (string), flag (string or empty). Example: {\"category\": \"Pothole\", \"priority\": \"Urgent\", \"reason\": \"Child fell into large pothole on Main Street.\", \"flag\": \"\"}"
    error_handling: "If description is empty or null, return error. If ambiguous between multiple categories, set category: Other and flag: NEEDS_REVIEW. If severity keywords present but not explicitly about injury/risk, still classify as Urgent per rule. Never return a category not in the allowed list."

  - name: batch_classify
    description: Reads a CSV file of complaints, applies classify_complaint to each row, and writes results to output CSV with category, priority, reason, and flag columns.
    input: "Path to input CSV file with a 'description' column; path to output CSV file"
    output: "CSV file with columns: description, category, priority, reason, flag. One row per input complaint. All output categories must be in the allowed list."
    error_handling: "If input file is missing or format is invalid, raise error with file path. If description column is absent, raise error. Skip rows with empty description and log count. If output path is not writable, raise error. Gracefully handle encoding issues and log warnings."
