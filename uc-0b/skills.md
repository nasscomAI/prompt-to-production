skills:
  - name: retrieve_policy
    description: >
      Loads a plain-text policy file and returns its content structured as
      a list of numbered sections, each with a section number, title, and
      list of clause texts.
    input: >
      file_path (string): filesystem path to a .txt policy document with
      numbered sections and clauses.
    output: >
      A list of dicts, each with keys: section_number (string, e.g. "2"),
      section_title (string, e.g. "ANNUAL LEAVE"), clauses (list of dicts
      each with keys: clause_id (string, e.g. "2.3"), text (string, the
      full clause text)).
    error_handling: >
      If the file does not exist, raise FileNotFoundError. If the file
      cannot be parsed into numbered sections, return an empty list and
      print a warning to stderr.

  - name: summarize_policy
    description: >
      Takes structured policy sections and produces a compliant plain-text
      summary that preserves every clause's binding obligations, references
      clause numbers, and flags verbatim quotes where summarisation would
      lose meaning.
    input: >
      sections (list of dicts): output from retrieve_policy, each with
      section_number, section_title, clauses (list of {clause_id, text}).
    output: >
      A string containing the full policy summary, organised by section,
      with each clause referenced by its clause_id and its obligation
      preserved.
    error_handling: >
      If a clause cannot be summarised without potential meaning loss,
      include it verbatim and prefix it with [VERBATIM]. Never skip clauses
      or output an empty summary.
