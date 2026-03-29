# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

# Agent Skills: Data Extraction & Validation

skills:
  - name: Entity_Parser
    description: Identifies and extracts specific nouns and alphanumeric strings from raw text transcripts.
    input: Raw text string (customer interaction transcript).
    output: A dictionary of identified entities (Order_ID, Product_Name, Date).
    error_handling: If an entity is partially identified but incomplete, it returns null for that specific key.

  - name: Date_Standardizer
    description: Converts various human-readable date formats into a strict ISO-8601 YYYY-MM-DD format.
    input: Text string representing a date (e.g., "March 16th").
    output: Formatted date string (e.g., "2026-03-16").
    error_handling: If no date can be identified, it returns the string "unknown_date" to avoid hallucination.

  - name: JSON_Formatter
    description: Packages all extracted and validated data points into a clean, machine-readable JSON structure.
    input: A list of validated data key-value pairs.
    output: A valid JSON object.
    error_handling: If the resulting JSON is empty, it returns a standard error message: {"error": "no_data_extracted"}.
