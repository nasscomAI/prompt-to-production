# skills.md

skills:

- name: classify_complaint
  description: >
  Classifies a single complaint using the description field into a fixed category,
  assigns priority based on severity keywords, generates a reason citing the text,
  and flags ambiguous cases.
  input: >
  A dictionary representing one complaint row with at least:
  - complaint_id (string)
  - description (string, may be empty or null)
    output: >
    A dictionary with keys:
  - complaint_id (string)
  - category (one of predefined categories)
  - priority (Urgent, Standard, or Low)
  - reason (one sentence citing words from description)
  - flag (either NEEDS_REVIEW or empty string)
    error_handling: >
    If description is missing, null, or empty, return:
  - category: Other
  - priority: Low
  - reason: "No description provided"
  - flag: NEEDS_REVIEW
    If multiple categories match or classification is unclear, assign:
  - category: Other
  - flag: NEEDS_REVIEW

- name: batch_classify
  description: >
  Processes an input CSV file of complaints, applies classify_complaint to each row,
  and writes the results into an output CSV file without crashing on invalid rows.
  input: >
  - input_path: string (path to input CSV file)
  - output_path: string (path to output CSV file)
    output: >
    A CSV file with columns:
    complaint_id, category, priority, reason, flag
    containing one classified row per input complaint.
    error_handling: >
    If a row is malformed or causes an exception:
  - Do not stop execution
  - Output a fallback row with:
    category: Other
    priority: Low
    reason: "Error processing row"
    flag: NEEDS_REVIEW
    If input file is missing or unreadable, raise an appropriate error.
