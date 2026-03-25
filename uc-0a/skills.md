# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint based on severity keywords and rigid taxonomy.
    input: Dictionary containing 'complaint_id' and 'description' keys.
    output: Dictionary containing 'category', 'priority', 'reason', and 'flag' keys.
    error_handling: If input format is invalid or description is missing, logs an error and returns None or safe defaults with NEEDS_REVIEW flag.

  - name: batch_classify
    description: Reads a batch of complaints from an input CSV, classifies them each, and writes them to an output CSV.
    input: String path to the input CSV and string path to the output CSV.
    output: Writes parsed and classified data to the output path without returning a value.
    error_handling: Handles missing files or invalid rows by logging warnings, ensuring the overall process continues without crashing.
