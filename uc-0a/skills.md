skills:
  - name: classify_complaint
    description: Classify a single complaint row to extract its category, priority, justification reason, and ambiguity flag.
    input: A complaint description string.
    output: A structured object/dictionary with keys category (Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, or Other), priority (Urgent, Standard, Low), reason (one sentence citing specific words), and flag (NEEDS_REVIEW or blank).
    error_handling: If the input is empty or the category is genuinely ambiguous, set the category to 'Other' and the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Read citizen complaints from an input CSV file, apply classify_complaint to each row, and write results to an output CSV file.
    input: Path to the input CSV file.
    output: Path to the output CSV file containing original fields along with classification fields (category, priority, reason, flag).
    error_handling: If the file is missing or has headers that are unsupported, raise a descriptive exception. Handle row-level errors gracefully.
