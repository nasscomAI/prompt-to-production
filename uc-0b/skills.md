# UC-0B Policy Summary Skills

skills:
  - name: retrieve_policy
    description: Read a policy text file and return its numbered clauses as structured data.
    input: A file path to a .txt policy document.
    output: A list of objects containing clause numbers and their associated text.
    error_handling: If the file is missing or unreadable, raise a clear error and stop processing.

  - name: summarize_policy
    description: Build a clause-preserving summary that includes the relevant numbered clauses and all of their conditions.
    input: A list of clause objects from retrieve_policy.
    output: A plain-text summary that preserves the source wording for the required clauses.
    error_handling: If a targeted clause is missing from the source, report it explicitly rather than guessing.
