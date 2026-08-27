skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes content by document name and section number.
    input:
      type: list of file paths
      format: plain text .txt files
    output:
      type: indexed dictionary
      format: document name → section number → section content
    error_handling: >
      If a file is missing or unreadable, report the specific filename
      and halt — do not proceed with partial document set.

  - name: answer_question
    input:
      type: string
      format: natural language question from staff
    description: Searches indexed documents for a single-source answer and returns it with citation, or returns the refusal template.
    output:
      type: string
      format: answer with citation (document name + section number) OR refusal template verbatim
    error_handling: >
      If answer requires combining two documents — return refusal template.
      If question matches no section in any document — return refusal template.
      Never guess, infer, or hedge.