# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses its content into structured numbered sections.
    input: Path to the .txt policy file.
    output: A dictionary or list of objects representing each numbered clause and its content.
    error_handling: Returns an error message if the file is not found or is in an unreadable format.

  - name: summarize_policy
    description: Takes the structured sections and produces a compliant summary that preserves all obligations and conditions.
    input: Structured sections of the policy.
    output: A string containing the summarized policy with clear clause references.
    error_handling: Flags clauses that are too complex to summarize without meaning loss.
