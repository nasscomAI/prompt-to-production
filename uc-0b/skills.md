# skills.md

skills:
  - name: retrieve_policy
    description: Load a policy text file and return the contents structured into numbered sections.
    input: Path to the policy text file (string).
    output: A dictionary or list of structured sections (e.g., matching section numbers to text contents).
    error_handling: If the file is not found or cannot be read, raise an error.

  - name: summarize_policy
    description: Take structured sections of a policy and produce a compliant summary that preserves all clauses and multi-condition obligations, with clause references.
    input: Structured sections of the policy (dictionary or list).
    output: A summarized text output containing every numbered clause with its exact constraints preserved, quoting and flagging any section that cannot be summarized without meaning loss.
    error_handling: If sections are missing or malformed, log the validation failure, refuse to summarize, or flag the missing sections.
