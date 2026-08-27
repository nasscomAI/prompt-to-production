# skills.md

skills:
  - name: retrieve_policy
    description: Loads a plain text policy file from disk and returns its content as structured, numbered sections.
    input: File path of the policy document.
    output: Structured representation of numbered sections and their corresponding text.
    error_handling: Return an error if the file cannot be located or read.

  - name: summarize_policy
    description: Summarizes structured policy sections into a compliant, condensed format, ensuring clause references are strictly maintained.
    input: Structured policy sections.
    output: A summary text document containing references to the original clauses.
    error_handling: Return an error if the input sections are malformed or cannot be parsed.
