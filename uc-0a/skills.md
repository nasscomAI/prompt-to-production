skills:
  - name: load_complaints
    description: Reads the complaint dataset from a CSV file and converts each row into a structured dictionary.
    input: CSV file path containing complaint records (complaint_id, complaint_text, location if present).
    output: List of dictionaries where each dictionary represents a complaint row.
    error_handling: If the file cannot be opened or required columns are missing, return an error message and stop processing.

  - name: classify_complaint
    description: Analyzes the complaint text and assigns category, priority, reason, and flag based on keyword rules.
    input: Dictionary containing complaint fields such as complaint_id and complaint_text.
    output: Dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If complaint_text is empty or unclear, return category "Other", priority "Low", and flag "NEEDS_REVIEW".