skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: A file path string pointing to a .txt policy document.
    output: A list of dicts, each with `clause_id` (str) and `text` (str), representing each numbered clause.
    error_handling: If the file does not exist, raise FileNotFoundError. If the file contains no numbered clauses, return an empty list.

  - name: summarize_policy
    description: Takes structured clause sections and produces a compliant summary preserving every clause with all original conditions.
    input: A list of dicts from `retrieve_policy` (each with `clause_id` and `text`).
    output: A single string containing the summary with clause references. Must satisfy enforcement rules (no omissions, no condition drops, no scope bleed, verbatim quoting with [VERBATIM] flag when needed).
    error_handling: If input is not the expected list-of-dicts format, raise TypeError. If a clause cannot be summarised without loss, quote it verbatim and flag it with [VERBATIM] rather than silently omitting or softening.
