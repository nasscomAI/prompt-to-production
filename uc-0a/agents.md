# Complaint Classification Agent

## Purpose
The agent classifies city complaints from the dataset and assigns them to the correct category and severity level.

## Responsibilities
1. Read complaint text from the dataset.
2. Identify the complaint category.
3. Detect severity keywords.
4. Assign priority level based on severity.
5. Produce classified output for further processing.

## Classification Rules

### High Severity
- Complaints involving hospitals
- Complaints involving schools
- Complaints involving injuries or safety risks

### Medium Severity
- Water leakage
- Garbage issues
- Drainage blockage

### Low Severity
- Streetlight not working
- Road maintenance
- Minor infrastructure complaints

## Output
The agent generates classified complaint records that will be used by the classifier system.
