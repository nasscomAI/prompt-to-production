
skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a standardized category, determines priority using severity triggers, generates a cited justification, and flags ambiguous cases.
    input: Dictionary (dict) containing a single complaint row with keys including 'complaint_id', 'location', and 'description'.
    output: Dictionary (dict) with keys 'complaint_id', 'category' (one of 10 allowed categories), 'priority' (Urgent, Standard, or Low), 'reason' (single sentence citing description text), and 'flag' (NEEDS_REVIEW or blank).
    error_handling: If the complaint description is missing, empty, or genuinely ambiguous, set category to 'Other' and flag to 'NEEDS_REVIEW'; strictly reject taxonomy drift and hallucinated sub-categories by defaulting invalid categories to 'Other'; escalate priority to 'Urgent' if any severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) is present; ensure reason is never omitted.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, runs classify_complaint on each row, and writes the resulting classifications to an output CSV file.
    input: Two file path strings representing input_path (path to input CSV file) and output_path (path to output CSV file).
    output: CSV file written to output_path containing classified records with columns 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: Safely handles null values, malformed lines, and unreadable rows without crashing; flags bad rows and ensures the output CSV is generated even if individual row classifications fail