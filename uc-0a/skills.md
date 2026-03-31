# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: parse_csv
    description: Reads the input CSV file into a list of dictionaries.
    input: file_path (string)
    output: list of dicts
    error_handling: Raise FileNotFoundError if input file does not exist.
    
  - name: classify_description
    description: Applies agent rules (keywords) to determine category, priority, reason, and flag.
    input: description (string), complaint_id (string)
    output: classified_dict (dict)
    
  - name: write_results
    description: Writes the list of classified dictionaries into a CSV file.
    input: results (list of dicts), output_path (string)
    output: None
    error_handling: Ensure directory for output_path exists.
