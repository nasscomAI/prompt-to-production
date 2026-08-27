
skills:
  - name: retrieve_policy
    description: Load a .txt policy file and return its content as structured numbered sections
    input: file_path (str) — path to a .txt policy document
    output: A list of dictionaries, each with keys: section_number (str), title (str), content (str)
    error_handling: If file is not found, raise FileNotFoundError with clear message. If file is empty, return empty list. If section numbering is inconsistent, preserve original numbering.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references, preserving all obligations and conditions
    input: sections (list of dicts) — output from retrieve_policy
    output: A string containing the full summary with all clauses referenced
    error_handling: If a section cannot be summarized without meaning loss, quote it verbatim and flag with [VERBATIM]. Never silently drop clauses or conditions.
