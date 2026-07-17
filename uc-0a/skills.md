skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row by category, priority, reason, and flag using LLM guidance and strict programmatic overrides.
    input: "dict containing complaint row fields (e.g., 'complaint_id', 'description')"
    output: "dict with keys: 'complaint_id', 'category', 'priority', 'reason', 'flag'"
    error_handling: "If the description is empty, null, or missing, set category to 'Other', priority to 'Standard', reason to 'No description provided', and flag to 'NEEDS_REVIEW'. If the category cannot be determined from description alone, set category to 'Other' and flag to 'NEEDS_REVIEW'. If description contains severity keywords ('injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse'), programmatically force priority to 'Urgent'."

  - name: batch_classify
    description: Read complaints from a CSV file, apply classify_complaint to each row, and write results to a CSV file.
    input: "Paths to the input CSV file and output CSV file (input_path: str, output_path: str)"
    output: "None (Writes output CSV file to output_path)"
    error_handling: "Do not crash on malformed CSV rows, empty/null descriptions, or API errors; log warnings, apply fallback defaults for failed rows, and produce the output CSV with all rows processed."
