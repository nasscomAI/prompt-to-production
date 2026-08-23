# skills.md

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file and returns its content as structured numbered
      sections for downstream processing.
    input: File path to a .txt policy document.
    output: >
      A list of structured sections, each with a clause number (e.g. "2.3") and
      its full text. Raises an error if the file does not exist or is not a .txt
      file.
    error_handling: >
      Logs error and raises FileNotFoundError if the path is missing.
      Raises ValueError if the file extension is not .txt.

  - name: summarize_policy
    description: >
      Takes structured policy sections and produces a compliant summary that
      preserves every clause, all conditions, and never adds external
      information.
    input: >
      A list of structured sections (clause number + text) as produced by
      retrieve_policy.
    output: >
      A plain-text summary string where every clause is represented, all
      conditions are preserved, and any clause that cannot be summarised
      without meaning loss is quoted verbatim and flagged [FLAGGED].
    error_handling: >
      Raises ValueError if input sections list is empty. Logs a warning for
      each clause that must be quoted verbatim due to meaning-loss risk.
