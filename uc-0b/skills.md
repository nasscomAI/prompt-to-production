skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and extracts its content, returning it as structured numbered sections.
    input: File path to the .txt policy document (String).
    output: A list of structured sections containing the clause numbers and their corresponding text (List of Objects/Dicts).
    error_handling: Refuses to read if the file is not a .txt file, is unreadable, or cannot be parsed into sections. Returns an error message detailing the failure.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references, strictly adhering to enforcement rules.
    input: A list of structured policy sections with clause numbers and text (List of Objects/Dicts).
    output: A summarized text document mapping to the input clauses, preserving all conditions and quoting verbatim if necessary (String).
    error_handling: Fails and flags if a section is incomprehensible. If output validation detects dropped conditions or added external info, returns an error prompting re-evaluation.
