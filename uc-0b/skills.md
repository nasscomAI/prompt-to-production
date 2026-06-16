skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content parsed into numbered sections keyed by clause number.
    input: File path string pointing to a .txt policy document.
    output: Ordered dict mapping clause numbers (e.g. "2.3") to their full text as a string.
    error_handling: If the file does not exist or cannot be read, exit with a clear error message stating the file path and reason. If no numbered clauses are found, exit with an error stating the document structure was not recognised.

  - name: summarize_policy
    description: Takes the structured sections from retrieve_policy and writes a compliant summary that preserves every clause, every binding verb, and every multi-condition obligation.
    input: Ordered dict of clause numbers to clause text (output of retrieve_policy), plus an output file path string.
    output: A .txt summary file where each line references the clause number followed by the obligation in the source's own binding terms.
    error_handling: If a clause cannot be condensed without dropping a condition or softening a verb, write the clause verbatim and append [VERBATIM — summarisation would alter meaning]. Never skip a clause silently.
