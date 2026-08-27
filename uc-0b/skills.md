# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns content as structured numbered sections.
    input: File path to policy_hr_leave.txt (string)
    output: Dictionary with numbered clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) as keys and exact clause text as values
    error_handling: Raises error if file not found, cannot be read, or does not contain all 10 required numbered clauses. Refuses to return partial results.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references, preserving all conditions and obligation verbs.
    input: Dictionary of numbered clauses with clause text (format from retrieve_policy output)
    output: Summary text with all 10 clauses and their core obligations intact, with explicit multi-condition preservation (e.g., "Department Head AND HR Director" for Clause 5.2)
    error_handling: If any clause is missing, any condition is silently dropped, any obligation verb is softened/synonymized, or any scope-bleed phrase appears (as is standard practice, typically, commonly, generally expected to), the skill refuses to output and flags the violation type with clause numbers for manual review.
