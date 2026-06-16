# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into category, priority, reason, and flag fields according to the enforcement rules in agents.md.
    input: >
      A single complaint row as a dict with at minimum a `description` field (string).
      Example: {"id": "001", "description": "Large pothole near school gate, child almost fell"}
    output: >
      A dict with four fields added to the input row:
        category  — exactly one of: Pothole, Flooding, Streetlight, Waste, Noise,
                    Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
        priority  — Urgent | Standard | Low
        reason    — one sentence quoting specific words from the description
        flag      — NEEDS_REVIEW | "" (blank)
      Example: {"id": "001", "description": "...", "category": "Pothole",
                "priority": "Urgent", "reason": "description contains 'school' and 'fell'", "flag": ""}
    error_handling: >
      If description is missing or empty, set category: Other, priority: Low,
      reason: "No description provided", flag: NEEDS_REVIEW.
      If category cannot be determined from the description alone, set category: Other
      and flag: NEEDS_REVIEW — never guess with false confidence.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to every row, and writes the classified results to an output CSV.
    input: >
      Two file paths (strings):
        input_path  — path to a CSV file with at minimum a `description` column
        output_path — path where the results CSV will be written
      Example: input_path="data/city-test-files/test_pune.csv", output_path="uc-0a/results_pune.csv"
    output: >
      A CSV file at output_path containing all original columns plus four new columns:
      category, priority, reason, flag — one row per input complaint.
      Also prints a summary to stdout: total rows processed, Urgent count, NEEDS_REVIEW count.
    error_handling: >
      If input_path does not exist or cannot be read, raise FileNotFoundError with a clear message.
      If the `description` column is absent from the CSV, raise ValueError naming the missing column.
      Rows with empty descriptions are passed through classify_complaint and will receive NEEDS_REVIEW flag.
