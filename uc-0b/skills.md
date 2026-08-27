skills:
  - name: retrieve_policy
    description: Loads the raw HR leave policy .txt file and returns the content as structured numbered sections.
    input: The file path to the policy document (string).
    output: A structured list or dictionary mapping numbered sections to their raw text content.
    error_handling: If the file cannot be found, cannot be read, or contains no numbered sections, aborts execution and raises a clear FileNotFoundError or ValueError.

  - name: summarize_policy
    description: Takes structured policy sections as input and produces a compliant, accurate summary with explicit clause references, ensuring no conditions are dropped.
    input: Structured policy sections (e.g., the output from retrieve_policy).
    output: A text string containing the final summary, with all conditions preserved and clauses referenced.
    error_handling: If a section is unparseable or its conditions cannot be accurately shortened without meaning loss, quotes the clause verbatim and flags it in the summary output.
