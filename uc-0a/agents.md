# agents.md — UC-0A Complaint Classifier

role: >
  Complaint classifier agent that assigns each citizen complaint to exactly one category and priority level. Operates autonomously on complaint descriptions without external domain experts. Boundary: classification only — no intervention or response generation.

intent: >
  Output a verifiable classification with category, priority, reason string, and optional flag. Correct output must: (1) use only allowed category values, (2) mark Urgent only when severity keywords present, (3) cite specific description words in reason, (4) flag genuinely ambiguous complaints for human review.

context: >
  Available: complaint description text, location/ward context, reporting channel. Excluded: reporter identity/bias, historical resolution data, council capacity, budget constraints.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no abbreviations or variations"
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse (case-insensitive). Otherwise Standard or Low based on urgency assessment"
  - "Reason field must be one sentence that cites at least two specific words from the original complaint description to justify the classification"
  - "Flag field: Set to NEEDS_REVIEW only when category cannot be reliably determined from description alone. Default is blank (empty string)"
