skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: A string representing the file path to the policy document.
    output: A list or dictionary mapping clause numbers to their exact text content.
    error_handling: If the file is missing or unreadable, raise a clear error and halt execution. If the formatting cannot be parsed, return the raw text with a warning.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary preserving all clauses and conditions.
    input: Structured policy sections (text or dictionary).
    output: A string containing the final summary adhering to the strict agents.md rules.
    error_handling: If a clause cannot be summarized without losing its meaning or conditions, quote it verbatim and flag it in the output instead of summarizing.
