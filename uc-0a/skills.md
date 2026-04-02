# UC-0A — Complaint Classifier Skills

## Skill: Text Classification

### Description
Ability to classify complaint text into predefined categories using keyword matching.

### Inputs
- Complaint text (string)

### Outputs
- Category (Sanitation, Road, Water, Other)
- Severity (Low, Medium, High)

### Rules
- Use keyword-based detection
- Match sanitation, road, water-related terms
- Assign High severity for sensitive locations (school, hospital, child)
- Assign Medium severity for serious indicators (many, urgent)

### Limitations
- Cannot understand complex language
- Depends on presence of keywords