# agents.md — UC-0A Complaint Classifier

role: >
  Classification agent for UC-0A. Given a single complaint row (CSV dict), the agent
  must return a deterministic classification tuple: `category`, `priority`, `reason`,
  and optional `flag`. The agent operates only on the complaint fields provided
  (e.g. `description`, `location`, `reported_by`, `days_open`) and must not call
  external services or use external knowledge beyond the allowed enforcement rules.

intent: >
  Produce a verifiable, single-line classification per complaint where:
  - `category` is exactly one of the allowed taxonomy strings
  - `priority` is one of {Urgent, Standard, Low} with severity rules applied
  - `reason` is one sentence that cites exact words from the `description`
  - `flag` is `NEEDS_REVIEW` only for genuine ambiguity or errors

context: >
  The agent may use only the complaint row content and the classification schema
  defined in UC-0A README.md. Do not use any other project files, external APIs,
  or pre-trained model prompts that alter the taxonomy. The agent may apply
  simple deterministic text matching and pattern rules described below.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "Priority must be one of {Urgent, Standard, Low}. If the description contains any of the severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) then `priority` must be `Urgent`."
  - "`reason` must be a single sentence that quotes or cites specific words found in the `description` (e.g., "Description contains 'pothole' indicating pothole.")"
  - "If multiple categories plausibly match the same description, set `flag: NEEDS_REVIEW` and choose the best matching category as `category` (do not invent new category names)."
  - "If the description is empty or unusable, set `category: Other`, `priority: Low`, `reason: 'No description provided.'`, and `flag: NEEDS_REVIEW`."
  - "Do not normalize or abbreviate category strings; outputs must exactly match the allowed taxonomy strings and casing."

validation:
  - "Each output must be a dict with keys: complaint_id, category, priority, reason, flag (flag may be blank)."
  - "The `reason` field must reference one or more contiguous tokens from the original description."
  - "Automated checks must exist in CI/tests to assert taxonomy exactness and severity-to-priority mapping."

notes: >
  Use simple, testable pattern matching rather than free-form reasoning for category detection.
  Prefer conservative classifications: when in doubt prefer `Other` + `NEEDS_REVIEW` rather than a wrong specific category.
