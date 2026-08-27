skills:
  - name: retrieve_policy
    description: Loads the HR leave policy and extracts numbered policy clauses.
    input: Path to a .txt policy file.
    output: Dictionary keyed by clause number with the exact clause text.
    error_handling: Raise a clear error if the file is missing or required clause numbers cannot be found.

  - name: summarize_policy
    description: Produces a clause-preserving HR leave summary from extracted policy sections.
    input: Dictionary of numbered sections from retrieve_policy.
    output: Plain-text summary containing every required UC-0B clause with preserved obligations and conditions.
    error_handling: Quote a clause verbatim and mark VERBATIM_REQUIRED if compression would drop a condition or alter meaning.
