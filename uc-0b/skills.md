# skills.md - UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: >
      Loads a plain-text policy file and returns its content parsed into
      structured numbered sections, preserving clause numbers and original text.
    input: >
      A string: file_path - the path to the .txt policy document to load.
    output: >
      A list of dicts, each with keys:
        - clause_id  (str)  - the clause number e.g. "2.3", "5.2"
        - heading    (str)  - clause heading if present, otherwise empty string
        - text       (str)  - full original text of the clause, unmodified
      Raises FileNotFoundError if the file cannot be read.
    error_handling: >
      If the file is missing or unreadable, raise FileNotFoundError with a
      descriptive message. If a section cannot be parsed into a clause number,
      include it with clause_id set to "UNSTRUCTURED" so it is never silently
      dropped.

  - name: summarize_policy
    description: >
      Takes the structured sections returned by retrieve_policy and produces a
      compliant clause-by-clause summary that preserves all obligations,
      conditions, and binding verbs exactly as they appear in the source.
    input: >
      A list of dicts as returned by retrieve_policy (each with clause_id,
      heading, text keys). Also accepts an optional output_path string; if
      provided, the summary is written to that file in addition to being
      returned.
    output: >
      A string containing the full summary. Each clause is referenced by its
      clause_id. If output_path is provided, the same content is written to
      that file. Returns the summary string in all cases.
    error_handling: >
      If the input list is empty, raise ValueError with message "No policy
      sections provided - cannot summarise empty document". If a clause text
      contains multiple interdependent conditions that cannot be condensed
      without meaning loss, include the clause verbatim with marker
      [VERBATIM - summarisation would alter meaning]. Never omit a clause
      because it is difficult to summarise.
