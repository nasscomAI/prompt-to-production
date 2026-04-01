# skills.md

## retrieve_policy
Purpose: load HR leave policy txt file.

Steps:
1. Read file
2. Split by numbered clauses
3. Extract:
   - clause number
   - text
   - obligation verb
   - conditions
   - deadlines
   - approvers

## summarize_policy
Purpose: produce clause-safe summary.

Steps:
1. Process one clause at a time
2. Preserve exact modality
3. Preserve all conditions
4. Preserve clause number
5. Preserve thresholds and deadlines
6. Preserve all approvers
7. Quote verbatim if compression risks meaning loss
8. Emit missing clause warning