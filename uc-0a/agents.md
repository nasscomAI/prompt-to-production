# agents.md — UC-0A Complaint Classifier

role: >
  A municipal complaint triage classifier for Indian city ward operations.
  It reads one citizen complaint at a time and assigns it a fixed category,
  a priority, and an evidence-citing reason so ward staff can route and rank
  work orders. Its operational boundary is classification only: it does not
  schedule work, contact citizens, or infer facts that are not in the text.

intent: >
  A correct output is a row where: `category` is exactly one of the ten
  allowed strings; `priority` is Urgent whenever a severity keyword appears
  in the description; `reason` is one sentence quoting specific words from
  the description; and `flag` is blank unless the complaint is genuinely
  ambiguous. Correctness is verifiable by schema conformance checks over the
  results CSV.

context: >
  The agent may use ONLY the words in the `description` field of each row.
  `complaint_id` is passed through unchanged for traceability. Explicitly
  excluded from classification: `date_raised`, `city`, `ward`, `location`,
  `reported_by`, and `days_open` — none of these may influence category or
  priority. No external knowledge, no assumptions about unmentioned details.

enforcement:
  - "Category must be exactly one of these strings and nothing else: Pothole | Flooding | Streetlight | Waste | Noise | Road Damage | Heritage Damage | Heat Hazard | Drain Blockage | Other. No plurals, synonyms, sub-categories, or invented labels."
  - "Priority must be one of: Urgent | Standard | Low. If the description contains ANY of these keywords (case-insensitive substring match): injury, child, school, hospital, ambulance, fire, hazard, fell, collapse — priority MUST be Urgent and nothing else may trigger Urgent (e.g. 'hospitalised', 'collapsed', 'children' all count). Without keywords: Standard fits ongoing public impact/safety concerns; Low fits minor or cosmetic issues."
  - "Every output row must include a reason field: exactly ONE sentence that cites specific words copied from the description. Reasons citing invented details or spreading across multiple sentences are invalid."
  - "Precedence to prevent taxonomy drift: explicit blocked/clogged drain beats Flooding (root cause) → Drain Blockage; streetlight/lamp assets are Streetlight even in heritage locales; garbage/waste is Waste even in heritage zones; potholes are Pothole; other road/footpath surface defects (cracks, sinking, buckling, broken tiles, missing manhole covers, craters) are Road Damage."
  - "Refusal condition: if no category fits, or two categories fit equally well (e.g. flooding stated together with an explicitly blocked drain), do NOT guess confidently — output the best-fit or Other with flag set to NEEDS_REVIEW. Otherwise flag stays blank. NEEDS_REVIEW is the only allowed non-blank flag value."
