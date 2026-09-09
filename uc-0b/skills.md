# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content split into structured numbered sections keyed by clause reference.
    input: str — path to the policy text file (e.g. policy_hr_leave.txt).
    output: dict — mapping of clause reference (e.g. "2.3") to the clause's core obligation and binding verb.
    error_handling: If the file is missing, unreadable, or a clause cannot be detected, raises a clear error rather than returning a partial or guessed inventory.

  - name: summarize_policy
    description: Takes the structured numbered sections from retrieve_policy and produces a compliant summary that references every clause and preserves all conditions.
    input: dict — clause-reference to obligation/verb mapping produced by retrieve_policy.
    output: str — summary text that includes a clause reference for every numbered clause, with all multi-condition obligations preserved verbatim in conditions and any meaning-loss clause quoted and flagged.
    error_handling: If a clause is missing from the structured input, refuses to emit a partial summary and reports the missing clause; if a clause cannot be summarised without meaning loss, quotes it verbatim and flags it.