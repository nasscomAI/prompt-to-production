# UC-0B Skills Definition

## Skill: Complete Clause Coverage
- Read every numbered clause in the source document
- Map each clause to at least one point in the summary
- Flag if any clause has no corresponding summary point

## Skill: Meaning Preservation
- Do not use words that soften obligations (e.g., "may" instead of "must")
- Do not merge clauses that have different conditions
- Preserve numerical values (days, amounts, percentages) exactly

## Skill: Structural Fidelity
- Maintain original section order
- Use the same section headings as the source document
- Keep all conditional logic ("if X then Y") intact

## Enforcement Rules
- Every numbered clause MUST appear in output — no exceptions
- Numbers and dates MUST match source exactly
- Modal verbs (must/shall/may) MUST match source exactly
