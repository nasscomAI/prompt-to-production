skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections keyed by section number.
    input: Absolute or relative file path to a plain-text policy document.
    output: A dictionary mapping section numbers (e.g. "2.3", "5.2") to their full text content as strings.
    error_handling: If the file does not exist or cannot be read, raise a FileNotFoundError with the path. If a section cannot be parsed, include it under key "UNPARSED" and continue.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant clause-by-clause summary with clause references, preserving all conditions and binding language exactly.
    input: A dictionary of structured sections as returned by retrieve_policy.
    output: A formatted plain-text summary string where each clause is summarised on its own line with its clause number, binding verb preserved, and multi-condition obligations kept intact.
    error_handling: If a clause cannot be summarised without meaning loss, output it verbatim annotated with [VERBATIM — risk of meaning loss if paraphrased]. Never skip a clause silently.
