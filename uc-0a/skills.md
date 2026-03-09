# UC-0A — Complaint Classifier · skills.md

## Skill: classify_complaint

### Purpose
Given a single complaint text string, return structured classification output.

### Signature
```
classify_complaint(complaint_text: str) -> dict
```

### Returns
```json
{
  "category": "Roads",
  "subcategory": "Pothole",
  "severity": "High",
  "reasoning": "Deep pothole blocking main road, risk of accident"
}
```

---

## Skill: read_csv_complaints

### Purpose
Read `test_hyderabad.csv` and return list of complaint dicts.

### Returns
List of rows: `[{complaint_id, complaint_text, ward}, ...]`

---

## Skill: write_results_csv

### Purpose
Write classified results to `results_hyderabad.csv`.

### Input
List of dicts with fields: `complaint_id, category, subcategory, severity, reasoning`

---

## Skill: apply_severity_override

### Purpose
Post-process severity — elevate to Critical if any Critical keyword found in complaint text.

### Critical Keywords
`injury, accident, hospital, child, school, death, fire, collapse, electrocution`

### Rule
If any keyword matches (case-insensitive), override severity to `Critical`.

---

## CRAFT Notes
- **C**ontext: Civic complaints from Hyderabad municipal data
- **R**ole: Classifier agent with keyword + override logic
- **A**ction: Classify → Override → Write
- **F**ormat: CSV in, CSV out
- **T**one: Neutral, deterministic, no hallucination
