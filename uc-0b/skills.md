skills:
  - name: retrieve_policy
    description: Reads a .txt policy file and parses its contents into structured, numbered sections for accurate referencing.
    input: File path string to a policy .txt document.
    output: A structured representation (e.g., JSON or dictionary) mapping clause numbers to their exact text.
    error_handling: If the file is unreadable or lacks clear numbered clauses, raise an error indicating the document structure is unsupported.

  - name: summarize_policy
    description: Takes structured policy sections and generates a concise summary that strictly preserves all conditions and references the original clause numbers.
    input: A structured representation of policy clauses (output from retrieve_policy).
    output: A text summary where every clause is addressed, conditions are maintained, and verbatim quotes are used for complex clauses, with a list of any flagged items.
    error_handling: If a summary cannot be generated without dropping conditions, the function must fallback to verbatim quoting of the difficult clauses and flagging them in the output.
