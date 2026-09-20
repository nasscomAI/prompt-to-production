skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason justification, and ambiguity flag.
    input: Dictionary (dict) containing string fields for complaint_id, description, ward, location, and other metadata.
    output: Dictionary (dict) containing complaint_id (str), category (str), priority (str), reason (str), and flag (str).
    error_handling: If input description is missing or invalid, output category 'Other', priority 'Low', reason 'Invalid or missing complaint description', and flag 'NEEDS_REVIEW'. If category is ambiguous or non-standard, map to 'Other' and set flag to 'NEEDS_REVIEW'. If severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) are present, enforce priority 'Urgent'. Prevent taxonomy drift and hallucinated sub-categories by restricting category strictly to the 10 allowed values.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, processes each row via classify_complaint, and writes the classified results to an output CSV file.
    input: String representing file paths for input CSV (--input) and output CSV (--output).
    output: Writes output CSV file containing headers complaint_id, category, priority, reason, flag.
    error_handling: If input file is missing or unreadable, raises FileNotFoundError with descriptive error. For individual row parsing errors or missing fields, flags the row with NEEDS_REVIEW and category Other rather than crashing the batch process.
