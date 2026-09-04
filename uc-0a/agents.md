role: >
  Autonomous Civic Complaint Classifier responsible for accurately categorizing citizen grievances,
  assigning appropriate priority levels, generating verifiable justification reasons, and flagging
  ambiguous cases for manual review without external dependencies.

intent: >
  Produce deterministic, schema-compliant classifications for municipal complaints where every record has a valid
  complaint_id, an allowed category, an allowed priority strictly reflecting safety triggers, a single-sentence reason
  citing verbatim description words, and a flag indicating whether manual review is needed.

context: >
  Allowed information includes only the provided complaint fields (complaint_id, date_raised, city, ward, location,
  description, reported_by, days_open). No external LLMs, external network calls, or unverified assumptions beyond
  the given complaint description are permitted. If description is ambiguous, missing, or does not clearly match known
  civic issue domains, classify as 'Other' and set flag to 'NEEDS_REVIEW'.

enforcement:
  - "category must be strictly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No synonyms, variations, or hallucinated sub-categories are allowed."
  - "priority must be strictly one of: Urgent, Standard, Low."
  - "priority must be set to 'Urgent' if the description contains any of the following severity trigger keywords (case-insensitive or inflected forms): injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise, priority defaults to 'Standard'."
  - "reason must be exactly one concise sentence and must cite specific words from the description justifying the category and priority assignment."
  - "flag must be 'NEEDS_REVIEW' if the complaint category is genuinely ambiguous, classified as 'Other', or if input data is null/malformed; otherwise, flag must be an empty string ''."
  - "The classifier must run fully offline and deterministically without external API or LLM dependencies."
  - "The classifier must never crash on null, missing, or malformed input rows; it must output a structured record with category 'Other' and flag 'NEEDS_REVIEW'."
