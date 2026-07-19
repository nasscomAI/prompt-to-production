skills:
  - name: retrieve_policy
    description: >
      Load a .txt policy file and return its content parsed into structured
      numbered sections with section headings and clause references preserved.
    input: >
      string — file path to a .txt policy document.
    output: >
      dict — keys are section numbers (e.g. "2", "3"), each value is a dict
      with "heading" (section title) and "clauses" (list of parsed clause
      objects with clause_id and text).
    error_handling: >
      If the file cannot be read or is empty, raise a clear error. If the file
      contains no numbered sections, return the raw text wrapped in a single
      section with id "0".

  - name: summarize_policy
    description: >
      Take structured policy sections and produce a compliant clause-by-clause
      summary that preserves every numbered clause, every condition, and every
      obligation without adding external information.
    input: >
      dict — structured sections from retrieve_policy with section headings
      and numbered clauses.
    output: >
      string — a section-by-section plain-text summary. Each numbered clause
      is represented with its clause reference and core obligation. Clauses
      that cannot be condensed without meaning loss are quoted verbatim and
      flagged [VERBATIM]. No external knowledge, no generalizations, no
      obligation softening.
    error_handling: >
      If the input is empty or malformed, return an error message. If a clause
      cannot be summarized without dropping conditions, quote it verbatim and
      flag it with [VERBATIM] rather than producing a lossy paraphrase.
