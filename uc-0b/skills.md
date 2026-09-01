# skills.md

skills:
  - name: retrieve_policy
    description: Loads the policy .txt file and returns its content as structured numbered sections.
    input: Path to policy_hr_leave.txt.
    output: A list/dict of sections, each keyed by clause number (e.g. "2.3") with its full text.
    error_handling: If the file is missing or a clause number cannot be parsed, raise a clear error rather than silently skipping content.

  - name: summarize_policy
    description: Takes structured clause sections and produces a compliant summary referencing every clause number, preserving all conditions and binding strength.
    input: Structured numbered sections from retrieve_policy.
    output: A summary text file (summary_hr_leave.txt) with one line per clause, prefixed by its clause number, preserving all conditions and the original obligation verb (must/will/requires/not permitted).
    error_handling: If a clause cannot be condensed without losing a condition or changing its binding strength, include the clause verbatim instead of paraphrasing it.