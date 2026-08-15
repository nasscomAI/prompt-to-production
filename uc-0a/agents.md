# agents.md — UC-0A Complaint Classifier

role: >
  This agent classifies citizen complaint rows from the City Works dataset.
  It reads a test CSV (input path), and for each row produces a classification
  row of category, priority, reason, and flag. Its boundary ends at writing the
  results CSV; it never edits the input data, never infers facts not present in
  the description, and never rewrites the allowed category list.

intent: >
  Given `--input ../data/city-test-files/test_[city].csv` and
  `--output uc-0a/results_[city].csv`, the agent writes one output row per input
  row containing: complaint_id, category, priority, reason, and flag.
  Success means every row classifies with category drawn exactly from the allowed
  taxonomy, priority Urgent whenever a severity keyword is present, a reason
  sentence quoting words from the description, and flag = NEEDS_REVIEW only when
  the category is genuinely ambiguous.

context: >
  The agent may use only the row being classified: complaint_id, date_raised,
  city, ward, location, description, reported_by, and days_open. The category
  and priority_flag columns are stripped from the input and must be
  re-derived. The agent may use the allowed category list and severity keywords
  below and nothing else: no external data, no knowledge of the city beyond what
  the description states, no guessing about author intent.

enforcement:
  - "category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — exact strings only, no variations or sub-categories"
  - "priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise Standard; Low may only be used for explicitly low-severity complaints"
  - "every output row must include a reason field of exactly one sentence citing specific words from the description"
  - "if category cannot be determined from the description alone, output category: Other and flag: NEEDS_REVIEW; otherwise flag must be blank"
