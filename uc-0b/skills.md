skills:
  - name: retrieve_policy
    description: Extracts the raw content of a policy document and splits it into numbered sections.
    input: File path (string) to the .txt policy source.
    output: A list of dict containing 'section_id' (string) and 'content' (string).
    error_handling: Raise a FileNotFoundError if the path is invalid or empty.

  - name: summarize_policy
    description: Compresses policy sections into concise summaries while retaining all binding clauses.
    input: List of sections (dicts) and a set of enforcement rules (strings).
    output: A markdown-formatted summary including all 10 mandated ground truth clauses.
    error_handling: If any of the 10 critical clauses are missing or lose meaning, quote them verbatim.
