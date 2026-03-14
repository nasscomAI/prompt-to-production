# skills.md

# Skills aligned with UC-0A Classification Schema
# Reference: README.md Classification Schema section

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a category and priority level with justification (one complaint row in → category + priority + reason + flag out).
    input: Dictionary with keys 'complaint_id' (string), 'location' (string), 'description' (string). The description contains the complaint text to analyze.
    output: Dictionary with keys 'complaint_id' (string, preserved from input), 'category' (exact string from allowed list - Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), 'priority' (Urgent/Standard/Low), 'reason' (string, one sentence citing specific words from description), 'flag' (string, 'NEEDS_REVIEW' or empty string).
    error_handling: If description is missing/empty, return category='Other', priority='Low', reason='No description provided', flag='NEEDS_REVIEW'. If category cannot be determined confidently from description text alone, return category='Other', flag='NEEDS_REVIEW', and explain in reason field. Must check for severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) case-insensitively and set priority='Urgent' if any are present. Never raise exceptions or skip rows.

  - name: batch_classify
    description: Reads complaints from input CSV file, applies classify_complaint to each row, and writes results to output CSV file (reads input CSV → applies classify_complaint per row → writes output CSV).
    input: Two string parameters - 'input_path' (path to CSV file with columns: complaint_id, location, description, where category and priority_flag columns are already stripped) and 'output_path' (path where results CSV should be written, typically results_[city].csv).
    output: Writes CSV file to output_path with columns: complaint_id, category, priority, reason, flag. Returns nothing (void function). Prints completion message "Done. Results written to {output_path}" to stdout.
    error_handling: If input file not found, print error message and exit with non-zero code. If input CSV is malformed, skip malformed rows and log warning to stderr but continue processing valid rows. If output path is not writable, print error and exit. Must produce output file with all 15 rows (typical city test file size) even if some individual classifications fail (use classify_complaint's error handling per row). Ensure consistent category naming across all output rows to prevent taxonomy drift.
