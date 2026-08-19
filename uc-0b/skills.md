# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a policy text file and returns its content as structured numbered sections.
    input: File path to the .txt policy file.
    output: A dictionary or structured list of numbered sections and their corresponding text.
    error_handling: If the file cannot be read, raise an error. If numbering is malformed, attempt to parse based on standard formatting or flag for review.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references.
    input: Structured sections from retrieve_policy.
    output: A text summary containing the core obligations, preserving all conditions and referencing the clause numbers.
    error_handling: If a requested clause is missing from the input, log a warning and note it in the output. If summarization risks meaning loss, output the clause verbatim with a flag.
