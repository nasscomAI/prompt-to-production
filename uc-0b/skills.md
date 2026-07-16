# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: file path (str) to a policy document whose clauses are numbered like 2.3, 5.2.
    output: ordered list of (clause_number, section_title, clause_text) tuples covering every numbered clause in the file.
    error_handling: Unreadable file → exits with a clear error. A file with no numbered clauses → exits with an error naming the expected format, never returns an empty structure silently.

  - name: summarize_policy
    description: Produces a clause-referenced summary in which every clause is present with all conditions and binding verbs intact.
    input: structured sections from retrieve_policy.
    output: plain-text summary grouped by section, one line per clause, each line starting with the clause number; unmappable clauses appear verbatim with a [VERBATIM — FLAGGED] prefix.
    error_handling: After writing, re-verifies that every input clause number appears in the output; if any clause is missing the program aborts with the missing clause numbers listed instead of shipping a lossy summary.
