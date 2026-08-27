skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and prepares the content as structured numbered sections for summarization.
    input: String path to the input policy text file.
    output: A string or list of strings containing the extracted clauses.
    error_handling: If the file cannot be read, raise a clear FileNotFoundError.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary preserving all multi-conditions and citing all clause numbers.
    input: The structured clauses extracted from the policy text.
    output: A formatted string containing the final summary, with clause numbers explicitly referenced.
    error_handling: If input text is empty or unparseable, return an error message asking for human review.
