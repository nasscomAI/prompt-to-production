skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into structured numbered sections for precise summarization processing.
    input: Absolute file path string to the policy document (e.g., policy_hr_leave.txt).
    output: A dictionary object where keys are section numbers and values are the corresponding text content.
    error_handling: Raises FileNotFoundError if the document is missing or inaccessible.

  - name: summarize_policy
    description: Generates a point-by-point summary that preserves all clause obligations and multi-condition dependencies without softening.
    input: Structured policy sections dictionary and RICE enforcement parameters.
    output: A summarized text document with clause references, ensuring zero condition omission.
    error_handling: Quotes clauses verbatim if summarization risks semantic meaning loss or obligation softening.
