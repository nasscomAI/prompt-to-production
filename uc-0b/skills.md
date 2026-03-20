skills:
  - name: retrieve_policy
    description: Loads a local .txt policy file and breaks it into a structured list of sections by number.
    input: file_path (string).
    output: List of section dicts: [{'section': '2.3', 'content': '...'}]
    error_handling: Return empty list if file not found; notify if sections cannot be parsed.

  - name: summarize_policy
    description: Processes a list of policy sections into a summary adhering to CMC strict-meaning guidelines.
    input: List of section dicts.
    output: String (summarized policy text with clause references).
    error_handling: If a key clause (e.g. 5.2) is missing from input, flag as INCOMPLETE in the output.
