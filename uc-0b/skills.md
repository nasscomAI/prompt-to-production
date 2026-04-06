skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses its contents into structured, numbered sections.
    input: File path to a valid `.txt` HR policy document.
    output: A structured text or JSON representation where each numbered clause is isolated and explicitly indexed.
    error_handling: Return a strict refusal if the file is unreadable, not a `.txt` file, or lacks a discernible numbered clause structure.

  - name: summarize_policy
    description: Generates a plain-text summary from structured sections while preserving every condition and obligation verbatim.
    input: Structured, numbered sections outputted by retrieve_policy.
    output: A plain-text summary document featuring 100% of the numbered clauses with zero omissions, strict multi-condition preservation, and verbatim quotes marked with [VERBATIM] where necessary.
    error_handling: Refuse to summarize if constraints (e.g., length limits) demand dropping any explicit approval conditions, clauses, or if the input isn't structured properly.
