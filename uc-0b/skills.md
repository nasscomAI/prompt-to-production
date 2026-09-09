skills:
  - name: retrieve_policy
    description: Loads the HR leave policy from a text file and returns its content as structured numbered sections.
    input: A .txt policy file containing numbered policy sections.
    output: Structured policy sections with their clause numbers and content.
    error_handling: If the file is missing, unreadable, or does not contain usable policy content, report the error and do not guess or create missing information.

  - name: summarize_policy
    description: Produces an accurate summary of the structured policy while preserving all clause requirements and conditions.
    input: Structured numbered policy sections from retrieve_policy.
    output: A concise policy summary with references to the original clause numbers.
    error_handling: If the input is incomplete, ambiguous, or a clause cannot be summarized without changing its meaning, flag the issue and quote the original clause instead of guessing.