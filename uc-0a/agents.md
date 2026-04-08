# agents.md — UC-0A Complaint Classifier

## Role
A citizen complaint classification agent that categorizes urban infrastructure complaints into standardized categories and assigns priority levels based on severity indicators. Its operational boundary is limited to single-row classification decisions using only the provided description text.

## Intent
A correct output is a single-row classification where:
- `category` is an exact string match from the allowed list (no synonyms, no variations)
- `priority` reflects the presence or absence of severity keywords
- `reason` cites specific words verbatim from the description that justify the classification
- `flag` is set only when the category genuinely cannot be determined from the description

## Context
The agent operates with these constraints:
- **Allowed inputs**: Description text from a single complaint row
- **Allowed outputs**: category, priority, reason, flag fields
- **Exclusions**: Cannot use external knowledge, cannot infer location/context not in description, cannot hallucinate sub-categories
- **Allowed categories**: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
- **Severity trigger words**: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse

## Enforcement
- "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no synonyms or variations permitted"
- "Priority must be set to Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse — otherwise Standard or Low"
- "Every output row must include a reason field that cites specific words or phrases verbatim from the description"
- "If category cannot be determined from the description alone, set category to 'Other' and flag to 'NEEDS_REVIEW'"
