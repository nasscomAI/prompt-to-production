---
name: classify-complaint
description: Classifies one complaint description into category, priority, reason, and optional flag
---

## What I do
- Take a single complaint description string
- Output structured classification: category, priority, reason, flag

## Input
- Complaint description: string

## Output
- category: one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
- priority: Urgent (if severity keywords present), Standard, or Low
- reason: one sentence citing specific words from the description
- flag: NEEDS_REVIEW or blank

## Error handling
- If category is genuinely ambiguous, set category to Other and flag NEEDS_REVIEW
