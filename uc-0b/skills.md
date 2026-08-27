# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content structured as numbered sections with clause references.
    input: A file path string pointing to a .txt policy document.
    output: A list of dictionaries, each with keys: section_number (str), section_title (str), clauses (list of dicts with clause_id and clause_text).
    error_handling: If file does not exist, raise FileNotFoundError. If file is empty, return empty list. If file has no numbered clauses, return full text as single unnumbered section with flag.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary preserving all numbered clauses and their exact obligations.
    input: A list of structured sections from retrieve_policy (list of dicts with section_number, section_title, clauses).
    output: A string containing the policy summary with clause references, preserving all obligations and conditions.
    error_handling: If input is empty, return "No policy content to summarize." If a clause cannot be summarized without meaning loss, quote it verbatim and append [VERBATIM] flag. Never skip clauses or add external information.
