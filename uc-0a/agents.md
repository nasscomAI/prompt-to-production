# UC-0A Complaint Classification Agents

## Agent 1 — Complaint Understanding Agent
Role:
Analyze complaint description text and identify keywords indicating issue type.

Responsibilities:
- Extract issue keywords
- Detect urgency signals (injury, hospital, child, hazard)
- Normalize complaint text

## Agent 2 — Category Classification Agent
Role:
Assign complaint to a valid category from the approved category list.

Responsibilities:
- Match complaint keywords to category taxonomy
- Prevent invalid category outputs
- Default to "Other" when classification uncertain

## Agent 3 — Priority Assessment Agent
Role:
Determine complaint urgency.

Rules:
- If safety keywords detected → Urgent
- Otherwise → Standard

## Agent 4 — Review Flag Agent
Role:
Detect ambiguous complaints.

Action:
- Flag "NEEDS_REVIEW" if category = Other or classification confidence low.