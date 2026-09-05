# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: Path to a .txt policy document (e.g. policy_hr_leave.txt).
    output: A structured representation with section and clause numbers (e.g. 2.3, 5.2) plus their text.
    error_handling: Raises an error if the file is missing, unreadable, or contains no numbered clauses.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references.
    input: Structured numbered sections as returned by retrieve_policy.
    output: A summary where every numbered clause is present, all conditions preserved, with clause references.
    error_handling: If a clause cannot be summarised without meaning loss, quotes it verbatim and flags it.