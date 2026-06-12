name: classify_complaint
description: Classifies a single complaint into category, priority, reason, and flag strictly using the predefined schema.
input:
type: object
format: a single complaint row containing a text description field
output:
type: object
format: fields include category (string), priority (string), reason (one sentence string), flag (string or blank)
error_handling:

If input is empty, invalid, or missing description, return category as Other, priority as Low, reason stating missing description, and flag as NEEDS_REVIEW
If no category from the allowed list can be confidently assigned, set category to Other and flag to NEEDS_REVIEW
If complaint text is ambiguous and could map to multiple categories, set flag to NEEDS_REVIEW and avoid confident classification
If severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) are present but not clearly linked to category, still assign priority as Urgent
If reason cannot cite specific words from complaint text, flag as NEEDS_REVIEW and include minimal extractive justification from input
Never generate categories outside the allowed list; fallback to Other if needed
If multiple conflicting classifications occur, resolve to single category or assign NEEDS_REVIEW flag



name: batch_classify
description: Reads input CSV, applies classify_complaint to each row, and writes structured output CSV.
input:
type: file_path
format: CSV file with complaint descriptions per row
output:
type: file_path
format: CSV file with columns category, priority, reason, flag written to specified output path
error_handling:

If input file is missing or unreadable, terminate with error indicating invalid input path
If CSV format is invalid or missing expected columns, terminate with error indicating invalid format
If any row is empty or malformed, process it using classify_complaint error handling rules
Ensure all rows produce output with all required schema fields; do not skip rows
If writing fails, return error indicating output path or permission issue
Ensure consistency of category values across rows; do not introduce variations for similar complaints