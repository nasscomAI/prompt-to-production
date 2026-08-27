# skills.md

skills:
  - name: retrieve_policy
    description: Loads a plain text HR policy file and returns its content structured as a list of numbered sections/clauses.
    input: file_path (string) - Path to the policy text file.
    output: sections (list of dicts) - Each dict contains "clause_id" (string) and "text" (string) representing the clause body.
    error_handling: Raises FileNotFoundError if the file doesn't exist, and ValueError if the file format is invalid or empty.

  - name: summarize_policy
    description: Takes structured numbered sections and generates a compliant, verified summary preserving all conditions for the 10 core clauses.
    input: sections (list of dicts) - The structured sections from the policy.
    output: summary (string) - A verified markdown summary mapping every required clause, preserving all conditions with explicit clause references, and quoting/flagging any clause where meaning would be lost if summarized.
    error_handling: Raises a ValidationError if any mandatory clauses are missing or if any multi-condition obligations are dropped or softened.
