# UC-0A — Complaint Classifier
Core failure modes: Taxonomy drift · Severity blindness · Missing justification · Hallucinated sub-categories · False confidence on ambiguity

## Classification Schema
| Field | Allowed values | Rule |
| :--- | :--- | :--- |
| **category** | Pothole · Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other | Exact strings only — no variations |
| **priority** | Urgent · Standard · Low | Urgent if severity keywords present |
| **reason** | One sentence | Must cite specific words from description |
| **flag** | NEEDS_REVIEW or blank | Set when category is genuinely ambiguous |

**Severity keywords that must trigger Urgent:** `injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`

## Skills to Define in skills.md
- **classify_complaint** — one complaint row in → category + priority + reason + flag out
- **batch_classify** — reads input CSV, applies classify_complaint per row, writes output CSV
