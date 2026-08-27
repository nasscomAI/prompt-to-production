skills:
  - name: retrieve_policy
    description: Load an HR policy text file, parse numbered clauses, and return them as a structured section dictionary.
    input: "Path to a .txt policy file containing numbered sections and narrative text."
    output: "A dictionary keyed by clause number, with the full clause text preserved as values."
    error_handling: "If the file is missing, unreadable, or lacks numbered sections, raise a clear ValueError instead of fabricating policy content."

  - name: summarize_policy
    description: Convert structured policy sections into a factual summary that enumerates the required clauses and preserves all conditions.
    input: "A structured dictionary of policy sections and a required-clause list from the UC specification."
    output: "A newline-separated summary string containing each required numbered clause and its binding obligation."
    error_handling: "If a required clause is absent, raise a validation error and do not silently omit it; if wording would be ambiguous, keep the original clause text verbatim."
