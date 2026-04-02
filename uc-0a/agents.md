# UC-0A — Complaint Classifier Agents

## Agent: Complaint Classification Agent

### Role
Classify citizen complaints into appropriate categories and severity levels.

### Responsibilities
- Read complaint text from CSV input
- Identify category based on keywords
- Determine severity using context clues
- Ensure consistent classification across all complaints

### Constraints
- Must not guess without keywords
- Must use clear rules for classification
- Must prioritize safety-related keywords (school, hospital, children)

### Failure Modes
- Missing severity for critical complaints
- Incorrect category assignment due to weak keyword detection