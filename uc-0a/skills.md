skills:

* name: classify_complaint
description: Classifies a single citizen complaint description row into a strict allowed category, priority level, one-sentence cited reason, and ambiguity flag.
input:
type: object
format: JSON object containing a 'description' key with a non-empty string value representing the complaint text.
output:
type: object
format: JSON object with keys 'category' (exact string: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, or Other), 'priority' (exact string: Urgent, Standard, or Low), 'reason' (single sentence string citing specific words from description), and 'flag' (exact string: NEEDS_REVIEW or empty string "").
error_handling: If input description is missing, invalid, or empty, return category 'Other', priority 'Standard', reason 'Missing or empty complaint description text.', and flag 'NEEDS_REVIEW'; if description contains any severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse), force priority to Urgent; if complaint text is genuinely ambiguous, set flag to NEEDS_REVIEW; if non-allowed category or sub-category hallucination occurs, force fallback to allowed exact strings or 'Other'.
* name: batch_classify
description: Reads an input CSV file of citizen complaints, applies classify_complaint sequentially per row, and writes the structured classification outputs to a specified target CSV file.
input:
type: object
format: JSON object containing 'input_path' (string path to input CSV file, e.g., ../data/city-test-files/test_pune.csv) and 'output_path' (string path to target CSV file, e.g., uc-0a/results_pune.csv).
output:
type: object
format: JSON object containing 'rows_processed' (integer count of classified rows), 'output_path' (string path to written file), and 'status' (string value 'SUCCESS' or 'FAILED').
error_handling: If input CSV file is unreadable or missing required description columns, raise FileNotFoundError and halt execution; if individual row processing fails, log the error, populate the row with default category 'Other', priority 'Standard', reason 'Failed to parse row.', and flag 'NEEDS_REVIEW', and continue processing remaining rows to guarantee complete CSV generation.