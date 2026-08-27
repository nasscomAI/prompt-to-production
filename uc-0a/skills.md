# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: [classify_complaint]
    description: Classifies a single citizen complaint into category, priority, reason, and flag based on the given schema rules.
    input: A dictionary of  a complaint row with  a 'description' field (string)
    output: A dictionary with keys 'category' (string from allowed list), 'priority' (Urgent/Standard/Low), 'reason' (one sentence citing words), 'flag' (NEEDS_REVIEW or empty string)
    error_handling: If the complaint is genuinely ambiguous, set flag to 'NEEDS_REVIEW'; otherwise, classify strictly using exact category names and priority rules. 

  - name: batch_classify
    description:  Reads an input CSV file of complaints, applies classify_complaint to each row, and writes the classified results to an output CSV file.

    input: input_csv_path (path to input CSV) and output_csv_path (path to output CSV). Two strings 

    output:  A string confirming success, e.g., "Classification complete. Output written to [output_csv_path]
    error_handling:  If input file not found, raise FileNotFoundError; if CSV format invalid, raise ValueError; ensure all rows are processed even if some fail.

    - name: validate_classification
    description: Verifies a classified complaint meets all schema constraints.
    input: Classified dict
    output: Tuple (bool, str) — True if valid, else False with error message
    error_handling: Check exact category match, keyword presence for priority, reason citation.

    constants:
    categories:[Pothole,Flooding, Streetlight,Waste,Noise,Road Damage, Heritage Damage,Heat Hazard,Drain Blockage,Other]

    urgent_keywords:[injury, \hild, school, hospital, ambulance, fire, hazard, fell, collapse]

