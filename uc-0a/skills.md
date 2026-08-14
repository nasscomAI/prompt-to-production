# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Analyzes a single complaint description and assigns category, priority, reason, and review flag according to the fixed classification schema and severity keyword rules.
    input: Dictionary with keys (complaint_id, description) where description is a string containing the citizen complaint text. All other fields from CSV row are ignored for classification.
    output: Dictionary with keys (complaint_id, category, priority, reason, flag) where category is one of 9 fixed values, priority is Urgent/Standard/Low, reason is one sentence citing description words, and flag is "NEEDS_REVIEW" or empty string.
    error_handling: If description is missing or empty, return category="Other", priority="Low", reason="No description provided", flag="NEEDS_REVIEW". If description contains no recognizable issue, return category="Other", flag="NEEDS_REVIEW" with reason explaining what is unclear. Never crash on malformed input.

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies classify_complaint to each row, and writes a results CSV with all classification outputs.
    input: Two file paths (strings) - input_path pointing to CSV with columns (complaint_id, description, ...) and output_path for writing results CSV.
    output: Writes CSV file to output_path with columns (complaint_id, category, priority, reason, flag). Returns nothing but prints summary statistics (total processed, flagged count, urgent count).
    error_handling: If input file not found, print clear error and exit. If a row fails to parse, log the complaint_id, mark as "NEEDS_REVIEW", and continue processing remaining rows. If output path is invalid, print error and exit. Ensure output file is created even if all rows fail - write headers at minimum.
