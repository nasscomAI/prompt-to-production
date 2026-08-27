# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Reads a policy text file and returns its numbered clauses as structured sections.
    input: Path to a .txt policy file.
    output: A dictionary of clause IDs to clause text, preserving the source wording for each numbered clause.
    error_handling: If the file is missing or contains no numbered clauses, raise a clear error and refuse to summarize.

  - name: summarize_policy
    description: Converts the retrieved clauses into a faithful summary that preserves all required clauses and their critical conditions.
    input: A dictionary of clause IDs to clause text plus a list of required clause IDs.
    output: A plain-text summary containing each required clause in a source-faithful form.
    error_handling: If any required clause is absent, raise an error and report the missing clause IDs.
