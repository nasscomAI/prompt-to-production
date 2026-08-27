skills:
  - name: retrieve_policy
    description: Reads the provided .txt policy file and extracts the content into structured, numbered sections.
    input: String representing the file path to the policy document (e.g., .txt file).
    output: A structured object or list containing the parsed text mapped to their respective numbered clauses.
    error_handling: If the file is missing or unreadable, raise an error or return a clear message indicating retrieval failure.

  - name: summarize_policy
    description: Takes the structured sections of the policy and generates a compliant summary with explicit clause references.
    input: Structured policy sections (text mapped to numbered clauses).
    output: A text summary ensuring every numbered clause is represented without scope bleed or condition drops.
    error_handling: If a clause is ambiguous or too complex to summarize safely, it is quoted verbatim and flagged.
