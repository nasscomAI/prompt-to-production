skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path (string) to a .txt policy document.
    output: An ordered dictionary mapping clause numbers (e.g. "2.3", "5.2") to their full clause text, preserving document order.
    error_handling: If the file does not exist or cannot be read, raise a clear error with the file path. If the file contains no parseable numbered sections, return an empty dictionary and log a warning. Ensure all numbered sections and subsections are captured without dropping any.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references preserving all binding obligations.
    input: An ordered dictionary of clause numbers to clause text, as returned by retrieve_policy.
    output: A list of summary lines, each prefixed with the clause number. Lines that cannot be safely compressed are marked with [VERBATIM] and reproduced exactly.
    error_handling: >
      Address failure modes: clause omission (verify every input clause appears in output),
      scope bleed (never add information not present in input text),
      condition dropping (verify multi-condition clauses like 5.2 preserve ALL conditions —
      e.g. "Department Head AND HR Director" must both appear).
      If a clause has multiple binding conditions that cannot be safely separated, flag it [VERBATIM].
