# skills.md — UC-0B HR Policy Analysis Skills

skills:
  - name: retrieve_policy
    description: Loads and parses the .txt policy document into structured numbered sections for easier analysis.
    input: File path to the policy document (.txt).
    output: List of dictionaries or structured object containing clause numbers and their raw text.
    error_handling: Refuses to process if file format is incorrect or numbered sections cannot be identified.

  - name: summarize_policy
    description: Generates a compliant summary by processing structured sections, ensuring full clause preservation.
    input: Structured policy sections (output from retrieve_policy).
    output: Text summary with explicit clause references and preserved conditions.
    error_handling: Flags sections that result in meaning loss during summarization for verbatim quoting.
