# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: >
      Loads a policy document from a .txt file path and returns its content
      as structured numbered sections (list of clause_id + text pairs).
    input: >
      input_path (str — path to a .txt policy document with numbered clauses)
    output: >
      list of dicts with keys: clause_id (str, e.g. "2.3"), section (str, e.g.
      "ANNUAL LEAVE"), text (str — full text of that clause)
    error_handling: >
      If the file does not exist or is empty, raise FileNotFoundError with
      a descriptive message. If a clause cannot be parsed, log a warning and
      skip it.

  - name: summarize_policy
    description: >
      Takes the structured clause list and produces a concise summary that
      preserves every clause from the 10-clause ground truth with all
      conditions intact. Clauses not in the ground truth may be omitted or
      grouped.
    input: >
      list of dicts with clause_id, section, text (as produced by
      retrieve_policy)
    output: >
      str — plain text summary with clause references, multi-condition
      obligations fully preserved, and [FLAG: verbatim] for any clause
      quoted due to meaning loss risk
    error_handling: >
      If the ground-truth clauses cannot be located, include the closest
      matching text and append [FLAG: clause_not_found]. Never raise an
      exception — always produce output.
