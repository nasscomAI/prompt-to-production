# skills.md

skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns its content as structured numbered sections (section number → heading + full clause text).
    input: file_path (path to a policy .txt file).
    output: An ordered list/dict of sections, each with section_number, heading, and clauses (clause_number → full clause text).
    error_handling: If the file is missing or unreadable, raises a clear error rather than returning an empty/partial structure silently — a missing source must not produce a summary that looks complete.

  - name: summarize_policy
    description: Takes structured sections from retrieve_policy and produces a compliant summary covering every numbered clause with all conditions intact.
    input: The structured sections dict/list from retrieve_policy.
    output: Plain text summary, one line per clause, in clause-number order, each line citing the clause number and preserving every condition/binding verb from the source.
    error_handling: If a clause's meaning cannot be condensed without loss, output the clause verbatim prefixed with "[VERBATIM — condensation would lose meaning]" instead of paraphrasing it away.
