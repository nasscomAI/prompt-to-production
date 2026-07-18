# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns its content as structured numbered sections.
    input: path (str, path to a policy .txt file).
    output: A dict of {clause_number: clause_text} plus {section_number: section_title}.
    error_handling: If a line cannot be matched to a clause or section, it is appended to the currently open clause's buffer rather than silently discarded, so no sentence is lost.

  - name: summarize_policy
    description: Takes structured sections from retrieve_policy and produces a compliant summary preserving every clause.
    input: The dict produced by retrieve_policy.
    output: A single string — the full summary text, one line per clause, prefixed with its clause number.
    error_handling: Asserts before writing that none of the known scope-bleed phrases appear in the output; raises rather than silently shipping a summary with invented content.
