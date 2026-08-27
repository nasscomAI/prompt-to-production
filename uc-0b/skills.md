# skills.md

skills:
  - name: retrieve_policy
    description: Loads a structured or unstructured `.txt` policy file and returns the content broken down by numbered sections for safe processing.
    input: file_path (string) pointing to the policy `.txt` file.
    output: A list of dictionaries or structured objects, each containing a section number and text body.
    error_handling: Refuses to load files that do not exist or are an unsupported format, raising a clear 'Policy Not Found' error.

  - name: summarize_policy
    description: Takes structured clauses and produces a meaning-preserving, highly literal summary that maintains all critical obligations and constraints.
    input: The output of retrieve_policy (structured sections).
    output: A single string or document containing the summarized clauses, preserving original referencing.
    error_handling: If a clause is highly ambiguous, it falls back to quoting the clause verbatim and adding a [NEEDS_REVIEW] tag.
