# Agents

## Complaint Classifier Agent

### Role
Classifies citizen complaints into categories with priority handling.

### Input
Complaint text from CSV file

### Output
Category (Water / Road / Sanitation / Other)

### Rules
- Detect keywords
- Handle critical cases (injury, hospital, school)
- Always assign a category

### Steps
1. Read complaint
2. Identify keywords
3. Apply rules
4. Return category