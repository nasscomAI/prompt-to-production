skills:
  - name: retrieve_policy
    description: Loads a plain text policy file and parses it into a structured list of numbered sections.
    input: File path to a .txt policy document.
    output: A list of objects containing clause numbers and their raw text content.
    error_handling: Refuses to process if the file is not found or is in an unsupported format.

  - name: summarize_policy
    description: Generates a concise summary of policy sections while ensuring no conditions or binding verbs are lost.
    input: Structured policy sections (list of objects).
    output: A bulleted summary string where each point references the source clause number and preserves all original obligations.
    error_handling: Flags clauses that are too legally dense to summarize without meaning loss and quotes them verbatim instead.
