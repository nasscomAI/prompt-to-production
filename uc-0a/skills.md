# skills.md — UC-0A Complaint Classifier
# Skill contracts grounded in README.md schema and agents.md enforcement

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag using the fixed UC-0A taxonomy.
    input: |
      A dict with at minimum two keys sourced from the input CSV
      (note: category and priority_flag columns are stripped from the CSV — never available here):
        complaint_id  (str)  — unique row identifier
        description   (str)  — free-text complaint description
    output: |
      A dict with exactly five keys matching the README classification schema:
        complaint_id  (str)  — echoed from input unchanged
        category      (str)  — one of: Pothole, Flooding, Streetlight, Waste, Noise,
                               Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
        priority      (str)  — one of: Urgent, Standard, Low
        reason        (str)  — one sentence citing specific words from the description
        flag          (str)  — "NEEDS_REVIEW" or empty string
    error_handling: |
      - If description is missing or empty: set category="Other", priority="Low",
        reason="No description provided", flag="NEEDS_REVIEW".
      - If category cannot be confidently determined: set category="Other",
        flag="NEEDS_REVIEW"; reason must still cite at least one word from the description.
      - Priority keyword check (injury, child, school, hospital, ambulance, fire, hazard,
        fell, collapse) must run before category assignment — never skip it.
      - Never raise an exception; always return a complete five-field output dict.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to every row, and writes a results CSV.
    input: |
      input_path  (str)  — path to a CSV file (e.g. test_[city].csv) with at least
                           complaint_id and description columns; category and
                           priority_flag columns are stripped and must not be read
      output_path (str)  — path where results CSV will be written (e.g. results_[city].csv)
    output: |
      A CSV file at output_path with columns in this order (matches README schema):
        complaint_id, category, priority, reason, flag
      One row per input row, including rows that encountered errors.
    error_handling: |
      - Rows with missing complaint_id or description are processed with classify_complaint's
        own error handling — they are never silently dropped.
      - If a row raises an unexpected exception during classification, write it with
        category="Other", priority="Low", reason="Classification error", flag="NEEDS_REVIEW".
      - If the input file cannot be opened, raise FileNotFoundError immediately.
      - Output file is always written as long as the input file was opened successfully.
