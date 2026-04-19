skills:
  - name: retrieve_policy
    description: Parses the .txt policy file, extracting and structuring the content into verifiable numbered clauses.
    input: File path to the .txt policy document (string).
    output: A structured dictionary/mapping of clause identifiers (e.g., '2.3') to their exact text content.
    error_handling: System terminates execution and explicitly reports an error if the specified file does not exist or cannot be read.

  - name: summarize_policy
    description: Generates a clear, compliant summary from the structured clauses, ensuring all multi-conditions remain intact and all clauses are referenced.
    input: The structured clauses dictionary (dict) and validation rules.
    output: A rigorously validated summary document (string) citing source clause numbers for every bullet point.
    error_handling: If any clause is too complex to summarize strictly without changing its meaning, output it verbatim wrapped in a [FLAG: Verbatim] marker instead of guessing.
