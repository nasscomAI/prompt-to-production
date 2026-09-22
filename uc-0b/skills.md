# skills.md

skills:

  - name: retrieve_policy
    description: Loads the HR leave policy and returns its numbered clauses as structured policy sections.
    input: Path to a UTF-8 .txt policy file.
    output: Structured collection of numbered clauses, with each clause containing its clause number and complete source text.
    error_handling: If the file is missing, unreadable, or contains no numbered clauses, report the error and do not generate a summary.

  - name: summarize_policy
    description: Produces a source-faithful summary of the structured policy while preserving every clause and all conditions.
    input: Structured numbered policy clauses extracted from the HR leave policy.
    output: Clause-by-clause text summary with the original clause references and all obligations, conditions, thresholds, deadlines, approvals, exceptions, and consequences preserved.
    error_handling: If the input is incomplete, ambiguous, or a clause cannot be summarized without losing meaning, preserve the source wording and flag the clause instead of guessing or omitting it.