# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as a list of structured numbered sections.
    input: Path to a .txt policy file (str).
    output: List of dicts, each with keys `section` (str, e.g. "2.3") and `text` (str, the clause body).
    error_handling: If the file is missing or unreadable, raise FileNotFoundError with the file path. If the file is empty, raise ValueError stating the file contains no content to summarise.

  - name: summarize_policy
    description: Takes the structured sections from retrieve_policy and produces a compliant clause-by-clause summary with clause references preserved.
    input: List of dicts with keys `section` and `text` (output of retrieve_policy).
    output: A plain-text summary string where each clause is referenced by its section number, all conditions are preserved, and binding verbs are not softened. Clauses that cannot be summarised without meaning loss are quoted verbatim and marked [VERBATIM — meaning loss risk].
    error_handling: If the input list is empty, return an error message stating no sections were provided. If an individual section has no text, skip it and append a warning line noting the missing section number.
