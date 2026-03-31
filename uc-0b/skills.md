skills:
  - name: retrieve_policy
    description: Loads a .txt HR policy file and returns its content organized as structured, numbered sections.
    input: The file path to the policy document as a string (.txt extension).
    output: A structured JSON or dictionary object containing sections and their corresponding original text.
    error_handling: Return a structured error message if the file is not found, cannot be read, or is empty.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary preserving all clauses, conditions, and obligations without scope bleed.
    input: Structured policy sections (JSON or dictionary format) containing explicit numbered clauses.
    output: A summarized text string with explicit clause references, ensuring no meaning loss or condition dropping.
    error_handling: Return an error if the input sections are malformed, missing required information, or impossible to summarize without meaning loss.
