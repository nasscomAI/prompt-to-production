skills:
  - name: retrieve_policy
    description: Loads a text policy file and parses its contents, returning structured numbered sections.
    input: Path to policy text file (string).
    output: A dictionary mapping section/clause numbers to their textual content.
    error_handling: Refuses and reports if the file is missing or unreadable.

  - name: summarize_policy
    description: Extracts the 10 target clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) and writes a compliant summary.
    input: Dictionary of parsed sections.
    output: Verbatim or near-verbatim summary string of all 10 clauses preserving all conditions.
    error_handling: Flags an error if any of the 10 target clauses are missing from the input data.
