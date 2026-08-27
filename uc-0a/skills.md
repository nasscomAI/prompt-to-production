# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single complaint row by category, priority, and justification based on the description text.
    input: "A dictionary with at least a 'description' field (string). Example: {'description': 'Pothole on Main Street near the bus stop, car damaged'}"
    output: "A dictionary with four fields: {'category': str, 'priority': str, 'reason': str, 'flag': str}. Category is one of the 10 allowed values; priority is Urgent/Standard/Low; reason is one sentence; flag is 'NEEDS_REVIEW' or empty string."
    error_handling: "If description is empty or None, return category='Other', priority='Standard', reason='No description provided', flag='NEEDS_REVIEW'. If description is ambiguous (does not clearly map to a category), return category='Other' and flag='NEEDS_REVIEW'."

  - name: batch_classify
    description: Reads a CSV file of complaints, applies classify_complaint to each row, and writes results to output CSV with original columns plus classification fields.
    input: "Path to input CSV file with columns including 'description'. Expects 15 rows per city; no header assumptions."
    output: "Path to output CSV file with all original columns plus four new columns: category, priority, reason, flag. Output uses same CSV format as input."
    error_handling: "If input file does not exist, raise FileNotFoundError with path in message. If a row has invalid description field, apply classify_complaint error handling for that row. Log row number and original description for any row that receives flag='NEEDS_REVIEW'."
