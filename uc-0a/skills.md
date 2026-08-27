# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint record into standard categories, sets priority, generates reason, and flags ambiguity.
    input: dict containing keys 'complaint_id', 'date_raised', 'city', 'ward', 'location', 'description', 'reported_by', 'days_open'.
    output: dict containing keys 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    error_handling: Returns 'Other' for category and sets 'flag' to 'NEEDS_REVIEW' if the input description is missing, empty, or does not clearly align with any specific category.

  - name: batch_classify
    description: Processes a CSV file of citizen complaints, applying classify_complaint to each row, and outputs a classified CSV file.
    input: input_path (str) to the source CSV file, output_path (str) to the target CSV file.
    output: Writes a CSV file containing headers 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    error_handling: Catches parse errors, handles empty rows gracefully by skipping them or inserting default unclassified rows with NEEDS_REVIEW flag, and ensures the script does not crash.
