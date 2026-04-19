skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured numbered sections.
    input: File path to the policy document (String).
    output: Structured text or JSON mapping clause numbers to their corresponding text.
    error_handling: If the file is missing or unreadable, throw an error. If the document has no clear numbered sections, return the raw text with a warning flag.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references, strictly adhering to the agent's enforcement rules (no condition drops, no scope bleed).
    input: Structured text or JSON containing numbered clauses (output from retrieve_policy).
    output: A comprehensive text summary containing all numbered clauses, preserving all multi-condition obligations and binding verbs.
    error_handling: If a clause cannot be summarized without losing meaning or softening obligations, quote the clause verbatim and append a [VERBATIM] flag.
