# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy text file and returns its content as structured numbered sections.
    input: Path to the .txt policy file.
    output: A list of dictionaries containing clause numbers and their corresponding text.
    error_handling: If the file is missing or empty, returns an error indicating the source is unavailable.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that preserves all obligations and conditions.
    input: A list of structured policy sections.
    output: A summary text where each point corresponds to a source clause, preserving all binding verbs and conditions.
    error_handling: If a clause cannot be summarized without meaning loss, it is quoted verbatim and flagged as [VERBATIM].
