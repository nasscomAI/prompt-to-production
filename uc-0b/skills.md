skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path string pointing to the .txt policy document.
    output: Structured representation of the policy document mapping section/clause numbers to their text.
    error_handling: Reports an error if the file is not found or if the document cannot be parsed into numbered sections.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references and fully preserved conditions.
    input: Structured policy sections (text mapped by clause numbers).
    output: A compliant summary string listing the core obligations and their respective clause numbers.
    error_handling: Flags and quotes the clause verbatim if the clause cannot be summarised without meaning loss or condition dropping.
