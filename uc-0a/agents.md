# agents.md — UC-0A Complaint Classifier

role: >
  The UC-0A Complaint Classifier is an AI agent that reads a single citizen complaint (text) and returns a validated classification record for municipal intake.

intent: >
  For each complaint the agent must output a record with the exact fields: `category`, `priority`, `reason`, and `flag`. Values must follow the Classification Schema in the README exactly so downstream systems can ingest results without mapping.

context: >
  The agent only uses the raw complaint `description` text provided in the input CSV. It must not access external databases, personal data, or additional context. Historical data may not be assumed.

output_schema: >
  - `category` (string): one of the exact values: Pothole · Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other
  - `priority` (string): one of the exact values: Urgent · Standard · Low
  - `reason` (string): one sentence justification citing specific words/phrases from the description
  - `flag` (string): either `NEEDS_REVIEW` when category is ambiguous, or blank

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No synonyms or variant spellings."
  - "Priority must be one of: Urgent, Standard, Low. Set `Urgent` when any severity keyword is present."
  - "Severity keywords that must trigger `Urgent`: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "`reason` must cite specific words or short phrases from the description (one sentence)."
  - "If the category cannot be determined from the description alone, set `category: Other` and `flag: NEEDS_REVIEW`. Do not guess a specific category when ambiguous."
  - "Do not invent sub-categories or additional output fields. Keep outputs deterministic and consistent."

skills_reference: >
  The workflows should implement at minimum the following skills defined in `skills.md`:
  - `classify_complaint`: input = one complaint row (description); output = `category`, `priority`, `reason`, `flag`.
  - `batch_classify`: reads the input CSV, applies `classify_complaint` per row, and writes the output CSV conforming to the schema above.

testing_notes: >
  When validating outputs, check for taxonomy drift (variant category names), severity blindness (urgent keywords classified as non-urgent), missing `reason`, and confident classifications on ambiguous descriptions. Follow the repository's commit formula when fixing failures.

usage: >
  - Input file: ../data/city-test-files/test_[your-city].csv (15 rows per city; `category` and `priority_flag` columns are stripped)
  - Output file: uc-0a/results_[your-city].csv

run_command: >
  python classifier.py \
    --input ../data/city-test-files/test_pune.csv \
    --output results_pune.csv
