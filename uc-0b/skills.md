# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads policy_hr_leave.txt and returns its content indexed by clause number.
    input: Path to a .txt policy file with numbered clauses (e.g. "2.3", "5.2").
    output: A dict mapping clause number (str) → clause text (str), covering every numbered clause found in the file.
    error_handling: If the file has no numbered clauses, returns an empty dict rather than raising — the caller then reports every required clause as missing.

  - name: summarize_policy
    description: Produces the required-clause summary from the indexed sections, per agents.md.
    input: The dict returned by retrieve_policy, plus the fixed list of 10 required clause numbers.
    output: A list of one line per required clause, in clause-number order, each starting with "[clause_number]".
    condition_rule: For clauses with multiple conditions (2.6, 5.2), the summary line must name every condition, not just one.
    softening_rule: The binding verb (must/will/requires/not permitted) must carry through unchanged in strength.
    error_handling: A required clause absent from the retrieved dict is written as "[clause_number] NOT FOUND in source document" — never silently skipped.
