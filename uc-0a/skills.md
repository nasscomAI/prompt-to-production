# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a category, priority level, reason, and ambiguity flag based on the complaint description text.
    input: >
      A dictionary (dict) representing one complaint row with at minimum a
      'description' field containing free-text complaint text. May also include
      'complaint_id' for pass-through identification.
    output: >
      A dictionary with exactly five keys:
        - complaint_id (str): the original complaint identifier, passed through unchanged.
        - category (str): exactly one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
        - priority (str): one of Urgent, Standard, or Low.
        - reason (str): a single sentence citing specific words from the description that justify the category and priority.
        - flag (str): 'NEEDS_REVIEW' if the category is genuinely ambiguous, otherwise an empty string.
    error_handling: >
      If the description field is null, empty, or contains only whitespace, return
      category as 'Other', priority as 'Low', reason as 'No description provided',
      and flag as 'NEEDS_REVIEW'. If the row is missing the description key entirely,
      apply the same fallback. The function must never raise an exception for bad input;
      it must always return a valid classification dict.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, classifies each row using classify_complaint, and writes the structured results to an output CSV file.
    input: >
      Two string arguments:
        - input_path (str): absolute or relative file path to a CSV file containing
          complaint rows. Expected columns include at least 'complaint_id' and 'description'.
        - output_path (str): absolute or relative file path where the results CSV
          will be written.
    output: >
      A CSV file written to output_path with one header row and one data row per
      complaint. Columns: complaint_id, category, priority, reason, flag.
      Returns None; the side effect is the written file.
    error_handling: >
      If a row cannot be parsed or causes an unexpected error, log the complaint_id
      (if available) and skip that row rather than crashing the entire batch. If the
      input file does not exist or is unreadable, raise a FileNotFoundError with a
      descriptive message. The output file must be written even if some rows fail,
      containing results for all successfully classified rows.
