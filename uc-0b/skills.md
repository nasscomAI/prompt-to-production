# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: clause_extraction
    description: Extracts and inventories all numbered clauses from the policy document, mapping core obligations and binding verbs to avoid clause omission.
    input: Text content of the policy document (string).
    output: List of dictionaries, each containing clause number, core obligation, and binding verb.
    error_handling: If no clauses found, return empty list and log warning.

  - name: summary_generation
    description: Generates a comprehensive summary that preserves all clauses, multi-condition obligations, and binding language without softening or omitting, ensuring exact meaning preservation.
    input: List of clause dictionaries from clause_extraction skill.
    output: Formatted text summary (string) covering all clauses without adding external information.
    error_handling: If input list is empty, return error message indicating no clauses to summarize.

  - name: summary_validation
    description: Validates that the generated summary includes all clauses, preserves all conditions and obligations, and adheres to enforcement rules against omission, scope bleed, and obligation softening.
    input: Original clause list and generated summary text.
    output: Validation report (dictionary) with boolean pass/fail and list of any missing or altered clauses.
    error_handling: If summary is empty, return fail with reason.
