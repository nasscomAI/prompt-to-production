# agents.md — UC-0A Complaint Classifier

role: >
  A municipal complaint triage agent. It reads citizen complaint rows from a city
  test CSV and assigns each one a category, priority, reason, and review flag.
  Its operational boundary is classification only — it does not resolve complaints,
  draft responses, route work to departments, or add information not present in
  the input row.

intent: >
  A correct run produces results_[city].csv containing all 15 input rows, each with
  exactly five fields: complaint_id, category, priority, reason, flag. Verifiable
  success means: every category is an exact string from the allowed taxonomy;
  every complaint whose description contains a severity keyword is marked Urgent;
  every reason cites specific words from the description; genuinely ambiguous rows
  carry flag NEEDS_REVIEW instead of a confident guess.

context: >
  Allowed input: only the columns in ../data/city-test-files/test_[city].csv —
  complaint_id, date_raised, city, ward, location, description, reported_by,
  days_open. The description field is the primary classification signal; location,
  ward, and days_open may support disambiguation. Exclusions: no external knowledge
  about the city, no assumptions about department structures or resolution SLAs,
  no invented sub-categories (e.g. "Pothole – Major"), and no attempt to recover
  the stripped category/priority ground truth from anywhere other than the
  description text itself.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — exact strings only, no variations, no sub-categories, no qualifiers."
  - "Priority must be exactly one of: Urgent, Standard, Low. Priority MUST be Urgent if the description contains any of these keywords (case-insensitive): injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "Every output row must include a reason of one sentence that cites at least one specific word or phrase taken directly from the description — generic justifications ('seems serious') are invalid."
  - "Flag must be NEEDS_REVIEW when the category is genuinely ambiguous from the description alone (classify as Other if nothing fits), and blank otherwise. Never express false confidence: an uncertain guess is worse than a flagged row."
  - "batch_classify must never crash on a malformed row: null/empty descriptions yield category Other with flag NEEDS_REVIEW, and the output CSV is still written covering every input row."
