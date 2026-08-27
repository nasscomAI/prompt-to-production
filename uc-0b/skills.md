skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file from a given path and returns its content
      as a structured list of numbered sections and clauses.
    input: >
      String — absolute or relative path to a .txt file on disk.
    output: >
      Dict — keys are section numbers (e.g. "2"), values are lists of
      clause dicts with keys "number", "text", and "binding_verb"
      (if identifiable).
    error_handling: >
      If the path does not exist, the file is not .txt, or the file
      is empty, raise a FileNotFoundError or ValueError with a clear
      message. Do not attempt to parse non-policy files.

  - name: summarize_policy
    description: >
      Takes structured sections (from retrieve_policy) and produces a
      plain-text summary containing every numbered clause with its
      obligation and all conditions preserved.
    input: >
      Dict — structured sections as returned by retrieve_policy.
    output: >
      String — plain-text summary. If a clause cannot be condensed
      without meaning loss, it is quoted verbatim and tagged [VERBATIM].
    error_handling: >
      If any clause from the input is missing from the output, raise a
      ValueError listing the missing clause numbers. If the input
      structure is malformed, raise a TypeError.
