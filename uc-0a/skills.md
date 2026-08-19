# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into category, priority, reason, and flag using the fixed schema and severity keyword rules.
    input: >
      A single complaint row as a dict with at minimum a `description` field (string).
      Example: { "id": "001", "description": "Water logging near school gate, child slipped and got injured." }
    output: >
      Dict with four fields:
        - category (string): exactly one of Pothole, Flooding, Streetlight, Waste, Noise,
          Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
        - priority (string): Urgent | Standard | Low
        - reason (string): one sentence quoting specific words from the input description
        - flag (string): NEEDS_REVIEW if category is ambiguous, otherwise blank
      Example: { "category": "Flooding", "priority": "Urgent", "reason": "Description mentions 'water logging' and 'child slipped and got injured' triggering Urgent.", "flag": "" }
    error_handling: >
      If description is missing or empty — return category: Other, priority: Standard,
      reason: "No description provided — cannot classify.", flag: NEEDS_REVIEW.
      If category cannot be determined from the description alone — return category: Other
      and flag: NEEDS_REVIEW. Never invent a category.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes a results CSV with the four classification fields appended.
    input: >
      - input_path (string): path to the source CSV file containing at minimum an `id`
        and `description` column.
      - output_path (string): path where the results CSV should be written.
    output: >
      A CSV file at output_path containing all original columns plus four appended columns:
      `category`, `priority`, `reason`, `flag`. One row per input complaint.
      Exits with a summary line to stdout: "Classified N rows. NEEDS_REVIEW: M."
    error_handling: >
      If input file is not found — print error and exit with code 1.
      If a required column (id, description) is missing from the CSV — print the missing
      column name and exit with code 1.
      Rows with empty descriptions are classified via classify_complaint error path
      (category: Other, flag: NEEDS_REVIEW) rather than skipped.
