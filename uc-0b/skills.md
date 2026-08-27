# skills.md

skills:
  - name: retrieve_policy
    description: Loads the raw .txt policy file and parses it into a structured format of numbered sections and content.
    input: String path to the policy file.
    output: List of dictionaries containing clause numbers and their text.
    error_handling: If the file is missing or unreadable, log an error and terminate the process.

  - name: summarize_policy
    description: Processes structured policy sections into a condensed summary while ensuring all obligations and conditions are preserved.
    input: Structured policy data (list of clauses).
    output: A summary document where every point corresponds to original clauses with preserved conditions.
    error_handling: If a clause contains ambiguous or conflicting instructions, quote it verbatim in the output.
