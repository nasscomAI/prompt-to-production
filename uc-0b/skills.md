skills:
  - name: retrieve_policy
    description: Load a plain-text policy file and return a structured list of numbered sections.
    input: path to .txt file (string)
    output: list of mappings with fields `number` (string) and `text` (string)
    error_handling: |
      - If the file is missing or unreadable, raise a FileNotFoundError with a clear message.
      - If numbering is ambiguous, return best-effort numbering and include a `__needs_review` flag for affected sections.

  - name: summarize_policy
    description: Produce a clause-by-clause summary that preserves binding verbs and multi-condition obligations.
    input: structured sections (list of mappings as returned by `retrieve_policy`)
    output: plain-text summary where each numbered clause is represented and any verbatim-quoted clauses are marked.
    error_handling: |
      - If a clause would lose meaning when summarised, include the original clause verbatim and add a clear `[VERBATIM_QUOTED]` flag.
      - If required sections are missing, raise a ValueError and list missing clause numbers.
