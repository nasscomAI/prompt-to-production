# skills.md — UC-0B Data Validator

## Skill: Field Validation
The agent must check required fields.

Required fields:
- complaint_id
- complaint_text

Rules:
- If complaint_id is empty → INVALID_ID
- If complaint_text is empty → NULL_TEXT


## Skill: Data Integrity
The validator must not modify the input text.

Rules:
- Do not change complaint text
- Do not generate new IDs
- Only report validation status


## Skill: Output Flags
Each row must contain a validation flag.

Possible flags:
- VALID
- INVALID_ID
- NULL_TEXT
- NEEDS_REVIEW


## Skill: Robust Processing
The validator must never crash.

Rules:
- If a row is malformed → flag NEEDS_REVIEW
- Continue processing remaining rows