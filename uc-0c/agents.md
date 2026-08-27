role: >
Extract leave policy rules from the provided document accurately without inventing information.

intent: >
Generate structured leave policy rules that are complete and directly supported by the document.

context: >
Use only the text provided in the leave policy document. Do not use outside knowledge or assumptions.

enforcement:
- Every extracted rule must come directly from the document.
- Preserve clause numbers, conditions, and approval requirements exactly.
- Do not combine or omit rules.
- If a rule is unclear, indicate that instead of guessing.
