skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file and returns its content as structured numbered sections,
      preserving section headers, clause numbers, and all condition text.
    input: File path (string) to a .txt policy document.
    output: List of section objects, each containing a section header and a list of
      clause dicts with number (str) and text (str).
    error_handling: >
      If the file does not exist or is not a .txt file, raise FileNotFoundError with
      the resolved path in the message. If the file has no numbered clauses, return
      an empty list and log a warning.

  - name: summarize_policy
    description: >
      Takes structured sections from retrieve_policy and produces a compliant plain-text
      summary that references every numbered clause, preserves all multi-condition
      obligations, never adds external information, and flags verbatim quotes when
    input: Structured sections output from retrieve_policy.
    output: Plain-text string summary with clause numbers in brackets, e.g. "[2.3]".
    error_handling: >
      If any clause text exceeds 300 characters and contains multi-part conditions,
      quote it verbatim and append [VERBATIM]. If the input sections list is empty,
      return a message stating no clauses were found.
