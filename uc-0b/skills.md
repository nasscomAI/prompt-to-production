skills:
  - name: retrieve_policy
    description: >
      Loads the policy text file and parses it into structured sections and
      individual numbered clauses with their corresponding text.
    input: >
      str (file_path) — path to the policy text document.
    output: >
      list of dicts — each dict represents a section with a 'title' (str)
      and a list of 'clauses' (each being a dict with 'number' (str) and 'text' (str)).
    error_handling: >
      If the input file path is invalid or the file does not exist,
      raises FileNotFoundError.

  - name: summarize_policy
    description: >
      Takes structured sections and clauses, processes each clause to apply
      a precise, condition-preserving summary, quotes/flags complex clauses,
      and returns the complete formatted summary.
    input: >
      list of dicts — structured sections and clauses from retrieve_policy.
    output: >
      str — a fully formatted summary document containing every clause,
      preserving all conditions, with verbatim-flagged quotes where necessary.
    error_handling: >
      If any clause is empty, raises ValueError. Skips empty sections.
