skills:

- name: classify_complaint
  description: Classifies a single citizen complaint into an allowed category and priority, provides a justification, and flags genuine ambiguity.
  input:
  type: complaint_row
  format:
  description: string
  output:
  type: classification_result
  format:
  category: "One of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  priority: "One of: Urgent, Standard, Low"
  reason: "Single sentence citing specific words from the complaint description"
  flag: "NEEDS_REVIEW or blank"
  error_handling:
  invalid_input:
  - "If description is missing, empty, or not a string, return category=Other, priority=Low, reason='Description missing or invalid.', flag=NEEDS_REVIEW"
  ambiguous_input:
  - "If multiple allowed categories are equally plausible or category cannot be determined with confidence, assign the best matching allowed category or Other and set flag=NEEDS_REVIEW"
  failure_modes:
  - "Use only exact category values from the allowed schema; never invent or vary category names"
  - "If description contains any severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse), set priority=Urgent"
  - "Always provide a reason field"
  - "Do not create hallucinated sub-categories"
  - "Do not express false confidence on genuinely ambiguous complaints"

- name: batch_classify
  description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes the classified output CSV.
  input:
  type: csv_file
  format:
  path: "../data/city-test-files/test_[city].csv"
  columns:
  - description
  output:
  type: csv_file
  format:
  path: "uc-0a/results_[city].csv"
  columns:
  - category
  - priority
  - reason
  - flag
  error_handling:
  invalid_input:
  - "If the input file is missing, unreadable, or not a valid CSV, stop processing and return a file access or format error"
  - "If a row is missing a valid description, process the row using classify_complaint invalid-input handling"
  ambiguous_input:
  - "Preserve NEEDS_REVIEW flags produced by classify_complaint"
  failure_modes:
  - "Apply classify_complaint independently to every row"
  - "Ensure all category values match the allowed schema exactly"
  - "Ensure severity keywords trigger Urgent priority"
  - "Ensure every output row contains a reason"
  - "Do not introduce new categories, columns, or sub-categories"
  - "Write the final output in CSV format with category, priority, reason, and flag fields populated for each row"
