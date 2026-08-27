# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into one of the ten predefined categories and sets its priority level based on severity keywords.
    input: A string containing the complaint description from a citizen.
    output: A structured result containing the category (string), priority (Urgent/Standard/Low), reason (one sentence citing source words), and flag (NEEDS_REVIEW or blank).
    error_handling: For ambiguous complaints that cannot be categorized, it assigns the category 'Other' and sets the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads complaint rows from a source CSV file, processes each using the classify_complaint skill, and writes the structured classification results to a target CSV file.
    input: The file path to the input CSV and the file path for the output CSV.
    output: A newly created CSV file containing the original rows enriched with category, priority, reason, and flag fields.
    error_handling: If the input file is missing or contains invalid data, it logs an error and terminates processing to prevent incomplete data outputs.
