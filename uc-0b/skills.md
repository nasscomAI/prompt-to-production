# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured, numbered sections.
    input: >
      file_path (str): The absolute or relative path to the policy text file.
    output: >
      A list of dictionaries representing structured sections, where each dict has:
        'clause_number' (str): e.g., '2.3'
        'text' (str): The full text of the clause.
    error_handling: >
      If the file cannot be found or read, log an error to stderr and return an empty list.
      If a line cannot be parsed as a numbered clause, append it to the previous clause.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: >
      clauses (list of dict): The output from retrieve_policy.
    output: >
      A single string containing the generated summary, formatted in markdown, with each
      clause explicitly referenced and its exact multi-party conditions and normative verbs preserved.
    error_handling: >
      If input clauses list is empty, return a string stating "No clauses provided to summarize."
      If a clause's meaning is highly complex, default to quoting it verbatim to prevent meaning loss.
