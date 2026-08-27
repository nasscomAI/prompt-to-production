# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections with clause IDs.
    input: A string argument: file_path (path to policy .txt file).
    output: A dictionary with keys: document_title (string), sections (list of dictionaries, each with clause_id, content, binding_verb).
    error_handling: If the file does not exist or cannot be read, raise FileNotFoundError with a descriptive message. If the file is empty, return an empty sections list.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that preserves all numbered clauses and their binding obligations.
    input: A dictionary with keys: document_title (string), sections (list of dictionaries with clause_id, content, binding_verb).
    output: A string containing the summary with all numbered clauses, preserving binding verbs and multi-condition obligations.
    error_handling: If any section is missing required fields, skip it and log a warning. If a clause cannot be summarised without meaning loss, quote it verbatim and flag with [VERBATIM].
