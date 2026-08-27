skills:
  - name: classify_complaint
    description: Classifies a single municipal complaint description into category, priority, reason, and flag following strict schema.
    input: Dictionary with keys 'complaint_id' (str), 'description' (str). Example: {'complaint_id': 'C1', 'description': 'Pothole on main road caused injury.'}
    output: Dictionary with keys 'category' (str exact match), 'priority' (str: Urgent/Standard), 'reason' (str one sentence), 'flag' (str or empty).
    error_handling: If description empty/invalid, return {'category': 'Other', 'priority': 'Standard', 'reason': 'Invalid or empty description.', 'flag': 'NEEDS_REVIEW'}; ambiguous cases also get Other + NEEDS_REVIEW.

  - name: batch_classify
    description: Reads input CSV (complaint_id, description), classifies each row using classify_complaint, writes output CSV (category, priority, reason, flag).
    input: Two strings - input_path (str to CSV), output_path (str to write CSV).
    output: None (writes file); prints success message.
    error_handling: Skips bad rows logging error, continues processing others; ensures output CSV created even if some rows fail.

