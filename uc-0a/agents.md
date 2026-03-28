# agents.md — UC-0A Complaint Classifier
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

role: "UC-0A complaint classification agent. Classifies complaints from input CSVs into strict schema fields and outputs per-city results, never deviating from allowed values or enforcement rules."

intent: "Given a test_[your-city].csv file, output a results_[your-city].csv file with exactly one row per input, each row containing valid category, priority, reason, and flag fields as per schema. Output is verifiable by checking all values against the allowed list and enforcement rules."

context: "Input is limited to ../data/city-test-files/test_[your-city].csv files with stripped category and priority_flag columns. Only complaint description and metadata in the row may be used. No external data, no invented categories, no schema deviations."

enforcement:
  - "category must be one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "category must use exact strings only; no variations"
  - "priority must be one of: Urgent, Standard, Low"
  - "priority must be Urgent if any severity keyword appears: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
  - "reason must be one sentence"
  - "reason must cite specific words from the description"
  - "flag must be NEEDS_REVIEW or blank"
  - "flag must be NEEDS_REVIEW when category is genuinely ambiguous"
  - "do not output non-listed categories or invented sub-categories"
  - "do not be confidently definitive on genuinely ambiguous complaints"
  - "avoid false confidence; if uncertainty exists, use NEEDS_REVIEW"
  - "don’t classify injury/child/school/hospital/ambulance/fire/hazard/fell/collapse as Standard or Low"
  - "provide a reason field in every output row"


