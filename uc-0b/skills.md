# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: nuance_preserved_summarization
    description: Distills complex policy text into actionable bullet points without losing legal constraints.
    input: Long-form text (HR Policy).
    output: Structured Markdown text with headings for Eligibility, Accrual, and Restrictions.
    error_handling: If conflicting rules are found in the text, list both and flag as 'POLICY_CONFLICT'.

  - name: constraint_extraction
    description: Identifies specific numbers, deadlines, and 'must/shall' requirements.
    input: HR Policy text.
    output: A list of mandatory constraints found in the document.
    error_handling: If no specific constraints are found, return 'No restrictive clauses identified'.