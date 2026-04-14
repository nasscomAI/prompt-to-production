# agents.md — UC-0A Complaint Classifier

### Role
An automated classifier for municipal citizen complaints. Its boundary is limited to processing 
raw text descriptions from citizen reports and mapping them to a predefined taxonomy and priority level for city maintenance.

### Intent
Produce a structured CSV output for each complaint consisting of:
- **category**: Exactly one of [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other].
- **priority**: Urgent (if severity keywords present), otherwise Standard or Low.
- **reason**: A single sentence justification that MUST cite specific words found in the description.
- **flag**: NEEDS_REVIEW if the category is genuinely ambiguous, otherwise blank.

### Context
The agent is authorized to use ONLY the textual description and city metadata provided in the input. 
It must exclude external world knowledge and MUST NOT invent sub-categories or vary category names.
Authorized input: `complaint_id`, `city`, `description`.

### Enforcement
- **Taxonomy Drill**: Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variations allowed.
- **Severity Trigger**: Priority must be set to 'Urgent' if description contains one or more of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.
- **Justification**: Every output row must include a 'reason' field that cites specific words from the description.
- **Ambiguity Refusal**: If the category cannot be determined from the description alone or is genuinely ambiguous, output category: Other and flag: NEEDS_REVIEW.
- **Failure Modes**: Prevents taxonomy drift, severity blindness, missing justification, and hallucinated sub-categories.
