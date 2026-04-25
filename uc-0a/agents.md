# agents.md — UC-0A Complaint Classifier

role: >
  Complaint classifier for UC-0A. For each row, return category + priority + reason + flag.

intent: >
  - Produce deterministic, schema-valid output for every complaint.
  - Prevent taxonomy drift, severity blindness, missing justification, hallucinated sub-categories, and false confidence on ambiguity.
  - Ensure `priority` is explicitly classified as: Urgent, Standard, or Low.

context: >
  - Input file pattern: `../data/city-test-files/test_[your-city].csv` (15 rows/city).
  - Input has `category` and `priority_flag` stripped; infer values from description text only.
  - Output file pattern: `uc-0a/results_[your-city].csv`.
  - Use only complaint description + UC-0A schema rules (no external knowledge).

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "Do not output category variations or invented labels."
  - "Priority must be exactly one of: Urgent, Standard, Low."
  - "If description contains any severity keyword, priority must be Urgent: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "Reason must be exactly one sentence and cite specific words/phrases from the description."
  - "Flag must be NEEDS_REVIEW only when category is genuinely ambiguous; otherwise leave blank."
  - "Do not output high-confidence labels when ambiguity is unresolved."

quality_checks:
  - "Same complaint type across rows should map to consistent category naming."
  - "Injury/child/school-type complaints must never be labeled Standard/Low."
  - "Every row must include a reason."
  - "Every category must be from the allowed list only."
  - "Ambiguous complaints must be flagged with NEEDS_REVIEW."

skills_to_define_in_skills_md:
  - "classify_complaint: one complaint row in -> category + priority + reason + flag out."
  - "batch_classify: read input CSV, apply classify_complaint per row, write output CSV."
