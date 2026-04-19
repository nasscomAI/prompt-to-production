# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a predefined category, determines priority level, provides a justification reason, and flags if review is needed.
    input: A dictionary representing a complaint row, containing at least a 'description' field with the complaint text.
    output: A dictionary with keys 'category' (string from allowed list), 'priority' (Urgent/Standard/Low), 'reason' (one sentence citing specific words), 'flag' (NEEDS_REVIEW or empty string).
    error_handling: If the category cannot be determined unambiguously from the description, set category to 'Other' and flag to 'NEEDS_REVIEW'. Ensure priority is Urgent if severity keywords are present.

  - name: batch_classify
    description: Reads a CSV file of complaints, applies classify_complaint to each row, and writes the classified results to an output CSV file.
    input: Path to the input CSV file (string), where each row has a 'description' column.
    output: Path to the output CSV file (string); writes a CSV with additional columns for category, priority, reason, and flag.
    error_handling: Skips rows with missing or invalid descriptions, logging errors; ensures all outputs adhere to the classification schema and enforcement rules.
