skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns its content as structured numbered sections.
    input: "file_path (str, path to a .txt policy document)"
    output: "list of dicts: [{clause: '2.3', text: '...'}], one entry per numbered clause found"
    error_handling: >
      If the file cannot be parsed into numbered clauses (no N.N pattern found), return the raw
      text as a single section with clause set to null rather than raising — let summarize_policy
      decide how to handle unstructured input.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: "list of {clause, text} dicts from retrieve_policy"
    output: "str — summary text, one line per clause, each line prefixed with its clause number"
    error_handling: >
      If a clause's text contains more than one obligation/condition (e.g. two required approvers),
      the output line must include all of them explicitly rather than collapsing to one — never
      silently drop a condition to keep the line short.
