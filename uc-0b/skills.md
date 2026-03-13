# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured numbered sections.
    input: File path string to the policy document.
    output: A list or dictionary of parsed clause numbers and their raw text content.
    error_handling: Return an empty list and log a read error if the file cannot be found or read.

  - name: summarize_policy
    description: Takes structured clause sections and produces a compliant summary preserving all conditions with clause references.
    input: Structured clauses (list/dict) from retrieve_policy.
    output: A single string containing the requested summary, explicitly referencing clause numbers.
    error_handling: If a clause is missing or ambiguous, quote it verbatim and prepend a [FLAG] tag.
