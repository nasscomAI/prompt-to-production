skills:
  - name: classify_complaint
    description: Classifies an individual municipal citizen complaint into standard taxonomy category, priority level, evidence justification, and review flag based on strict RICE rules.
    input: Dictionary containing keys 'complaint_id' and 'description' (optional fields: 'ward', 'location', 'date_raised').
    output: Dictionary containing exact keys 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    rule_enforcement:
      category: Must match exactly one of ['Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other'].
      priority: 'Urgent' if description contains any of ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']; otherwise 'Standard'.
      reason: Single sentence citing exact verbatim words from description and any matched severity triggers.
      flag: 'NEEDS_REVIEW' if description is empty, category matches multiple distinct categories, or category is 'Other'; otherwise empty string "".
    error_handling: If description is missing or invalid, assigns category 'Other', priority 'Standard', flag 'NEEDS_REVIEW', and logs reason.

  - name: batch_classify
    description: Reads a CSV file of citizen complaints, executes classify_complaint for each row, and writes structured outputs to a destination CSV file.
    input: String file path 'input_path' (pointing to input CSV) and string file path 'output_path' (target location for results CSV).
    output: Writes destination CSV with header ['complaint_id', 'category', 'priority', 'reason', 'flag'].
    error_handling: Catches row-level parsing or execution exceptions, emitting a fallback row with flag 'NEEDS_REVIEW' and error detail in 'reason' without interrupting batch execution.
