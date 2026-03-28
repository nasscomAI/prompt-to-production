# skills.md

skills:
  - name: retrieve_policy
    description: Opens and loads a `.txt` policy file and returns the content as structured, readable numbered sections.
    input: Filepath to the policy document (e.g., `../data/policy-documents/policy_hr_leave.txt`).
    output: A string containing the text of the entire policy document, correctly read from disk.
    error_handling: If the file is missing or corrupted, raise a `FileNotFoundError` or print an explicit error and stop.

  - name: summarize_policy
    description: Takes the structured sections and produces a compliant, condition-preserving text summary focusing on the 10 core clauses.
    input: The raw text string containing the policy clauses.
    output: A plain-text document clearly stating the summarized policy clauses.
    error_handling: If a specific clause is overly ambiguous or cannot be confidently summarized, quote it verbatim and append a [FLAGGED] note.
