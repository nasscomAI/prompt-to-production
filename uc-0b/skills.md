# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns content as structured numbered sections
    input: "input_path (str): path to policy .txt file"
    output: "dict with keys: sections (dict of clause_number -> content), full_text (str)"
    error_handling: "If file not found, raise FileNotFoundError. If file is empty, return empty dict."

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references
    input: "sections (dict): clause_number -> content, required_clauses (list): [2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2]"
    output: "str: summary text with all clauses preserved"
    error_handling: "If a clause cannot be summarised without meaning loss, quote it verbatim and add [FLAG: verbatim] marker"
