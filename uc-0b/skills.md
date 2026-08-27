# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses its contents into structured numbered clauses.
    input: file_path (str)
    output: dict or list of structured sections and clauses
    error_handling: Raises FileNotFoundError if file is missing or unreadable.

  - name: summarize_policy
    description: Produces a complete summary of all policy clauses preserving multi-condition requirements and binding terminology.
    input: policy_data (structured clauses)
    output: summary text (str) formatted section by section
    error_handling: Verifies all clauses are included and no multi-condition requirements are dropped.
