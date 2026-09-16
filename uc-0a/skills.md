# Skills: Complaint Processing & Severity Escalation

## Triggers & Keywords
- **Roads / Pothole:** Pothole, crater, broken road, asphalt hole.
- **Water:** Leakage, pipe burst, contamination, no water.

## Extraction Rules
- Extract the core issue description and location metadata if available.

## Severity Escalation Logic
- **Critical / High:** If the text contains keywords such as `injury`, `child`, `school`, `hospital`, `live wire`, or `accidental hazard`, automatically escalate the severity level to **High** or **Critical**, regardless of the basic category.