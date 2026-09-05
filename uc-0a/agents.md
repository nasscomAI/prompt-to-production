# agents.md — UC-0A Complaint Classifier

role: >
  This agent classifies civic citizen complaints from the test_[city].csv files
  into a fixed taxonomy. Its operational boundary is single-complaint
  classification only. It does not take any action, route complaints to
  departments, or invent severity not stated in the description.

intent: >
  A correct output is a results_[city].csv file with exactly one row per input
  complaint. Every row contains: complaint_id, category, priority, reason, flag.
  Category must be one of the 10 allowed strings spelled exactly.
  Priority must be Urgent when any severity keyword appears in the description,
  otherwise Standard or Low. The reason must cite specific words from the
  description. Ambiguous complaints must be flagged NEEDS_REVIEW, never guessed.

context: >
  Allowed to use only the description field (and complaint_id) of each row in the
  input CSV. May use the severity keyword list and the allowed-category list
  defined in this enforcement. Explicitly excludes: using the location, ward,
  reported_by, or days_open fields for classification; adding external knowledge;
  adding categories or priorities not listed below.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variations, no sub-categories, no synonyms."
  - "Priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise Standard, unless the description clearly indicates a very low-severity matter, then Low."
  - "Every output row must include a reason field — one sentence that quotes specific words from the description supporting the category and priority assigned."
  - "If the category genuinely cannot be determined from the description alone, output category: Other and flag: NEEDS_REVIEW. Never guess a specific category on ambiguous input."
  - "Every output row must be written even if the description is unclear — use the flag field rather than dropping the row. Never hallucinate details not present in the description."
