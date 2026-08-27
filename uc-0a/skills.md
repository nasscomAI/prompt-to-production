# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single complaint row to determine category, priority, and reason based on a predefined taxonomy and severity keywords.
    input: A dictionary representing a single row from the city test CSV.
    output: A dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: Returns category 'Other' and sets flag to 'NEEDS_REVIEW' if the description is blank or totally ambiguous.

  - name: batch_classify
    description: Orchestrates the processing of an entire CSV file, handling entry/exit and ensuring the output schema is strictly followed.
    input: Filesystem paths for input CSV and output results CSV.
    output: Writes a CSV file to the specified output path.
    error_handling: Handles missing files and ensures the process continues even if individual rows fail.
