skills:
  - name: retrieve_policy
    description: Loads a plaintext HR policy document and returns its content as a structured list of numbered sections.
    input: File path (string) to the strictly formatted .txt policy file.
    output: A structured object/list containing numbered sections and their corresponding verbatim text.
    error_handling: If the file is missing or unreadable, raise a FileNotFoundError or return a standardized error object. If the text lacks recognizable numbered clauses, return an error indicating the document is malformed.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that retains all core obligations and multi-condition requirements, citing clause numbers.
    input: Structured grouped sections (list of objects/strings) produced by retrieve_policy.
    output: A compiled summary text adhering to the strict enforcement rules, with explicit clause references.
    error_handling: If a clause's complexity prevents accurate summarization without meaning loss, output the original clause verbatim and append a "[FLAG: VERBATIM]" tag.
