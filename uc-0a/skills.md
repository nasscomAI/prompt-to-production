# skills.md — UC-0A Complaint Classifier

## Skill: Complaint Text Analysis
The agent must read the complaint description and identify important keywords
that indicate the type of civic issue being reported.

Examples:
- "pothole", "road broken", "street damaged" → Roads
- "water leakage", "pipeline broken", "no water supply" → Water
- "garbage", "trash", "waste not collected" → Sanitation

The agent must extract the most relevant issue mentioned in the text.


## Skill: Category Classification
The agent must classify every complaint into **exactly one category**.

Allowed categories:
- Roads
- Water
- Sanitation
- Other

Rules:
- If multiple keywords appear, choose the **most severe infrastructure issue**
- If no clear category exists → classify as **Other**
- Do not create new categories


## Skill: Priority Assignment
The agent must assign a priority level based on urgency words in the complaint.

Priority levels:
- Urgent
- High
- Medium
- Low

Rules:
- Urgent → injury, accident, flood, danger, school
- High → road damage, major water leak, blocked drainage
- Medium → garbage collection delay, minor leak
- Low → general complaints or unclear reports


## Skill: Reason Generation
Each classification must include a **reason** explaining why the category
and priority were assigned.

Rules:
- The reason must reference specific words from the complaint description
- The reason must be short and factual
- Example:
  "Detected keyword 'pothole' in complaint text"


## Skill: Data Validation
The agent must validate input rows before classification.

Rules:
- If complaint text is empty or null → flag: NULL_TEXT
- If complaint_id is missing → flag: INVALID_ID
- If classification cannot be determined → flag: NEEDS_REVIEW
- The program must not crash when encountering bad rows


## Skill: Output Formatting
The output CSV must contain the following fields exactly:

- complaint_id
- category
- priority
- reason
- flag

Rules:
- Each input row must produce exactly one output row
- Missing or invalid rows must still appear in output with an appropriate flag