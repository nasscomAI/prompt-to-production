# skills.md — UC-0C Complaint Router

## Skill: Category Interpretation
The agent must read the complaint category and determine the
responsible department.

Categories:
- Roads
- Water
- Sanitation
- Other

## Skill: Routing Logic
Routing rules:

Roads → Road Maintenance  
Water → Water Supply  
Sanitation → Waste Management  
Other → General Services

## Skill: Output Structure
Each row must include:

- complaint_id
- category
- department
- flag

## Skill: Error Handling
If category is missing or invalid:

flag → NEEDS_REVIEW

The program must not stop processing other rows.