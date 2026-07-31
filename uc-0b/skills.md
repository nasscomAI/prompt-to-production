skills:
  - name: retrieve_policy
    description: Reads the raw HR policy text file and parses it into structured numbered sections and clauses.
    input: Input file path to the text document (str)
    output: Dictionary mapping section titles to lists of numbered clauses
    error_handling: Raises FileNotFoundError with clear message if file does not exist.

  - name: summarize_policy
    description: Summarizes policy sections while preserving all mandatory binding verbs, multi-person approval constraints, and clause references.
    input: Structured policy sections dictionary
    output: Formatted string summary containing all section summaries and clause preservation markers
    error_handling: Quotes missing or complex clauses verbatim to prevent scope bleed or obligation softening.
