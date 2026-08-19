# agents.md — UC-0A Complaint Classifier

role: >
  Complaint Classifier agent — automatically categorises civic complaints
  into allowed taxonomy categories (Pothole, Flooding, Streetlight, Waste,
  Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other)
  and assigns priority (Urgent, Standard, Low) based on severity keyword
  triggers. Outputs a reason field citing specific description words and a
  flag indicating whether manual review is needed.

intent: >
  Given a complaint description, produce a structured output with exactly
  one category, a priority level (Urgent, Standard, Low), a reason citing
  matched keywords, and a flag (NEEDS_REVIEW or blank). Must flag null/empty
  descriptions or ambiguous categories as NEEDS_REVIEW. Must not crash on
  malformed rows. Must produce output CSV even when some rows fail.

context: >
  Input: rows from test_[city].csv with columns
  complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
  Description text is the primary source for classification. Keyword lists are
  fixed at runtime according to workshop specification.

enforcement:
  - Category must be exactly one of: Pothole, Flooding, Streetlight, Waste,
    Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other (case-sensitive).
  - Priority must be "Urgent" if description contains any of:
    injury, child, school, hospital, ambulance, fire, hazard, fell, collapse;
    otherwise "Standard" (or "Low" if minor).
  - Every output row must include a reason field (one sentence) citing specific
    words from the description that triggered the classification.
  - If category cannot be determined from description alone or is ambiguous,
    output category: Other and flag: NEEDS_REVIEW.
  - Null or empty description rows must be handled gracefully without crashing
    and assigned category: Other, priority: Standard, reason: "No description provided",
    flag: NEEDS_REVIEW.