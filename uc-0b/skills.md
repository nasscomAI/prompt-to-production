skills:
  - name: retrieve_policy
    description: Loads .txt policy file and returns content as structured numbered sections.
    input: File path to the .txt policy document (string).
    output: Structured representation of the policy clauses with their numbering.
    error_handling: Raises an exception if the file is not found, cannot be read, or contains improperly formatted sections.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured numbered policy sections.
    output: Summarized text conforming to all enforcement rules, preserving meaning and conditions.
    error_handling: Includes a verbatim quote and flags the clause if an obligation is too complex to summarize safely without dropping conditions.
