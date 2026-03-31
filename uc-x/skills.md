# skills.md

skills:
  - name: retrieve_documents
    description: Load all 3 policy .txt files and index them by document name and section number.
    input: List of file paths to the 3 policy documents.
    output: Indexed dictionary keyed by (document_name, section_number) → section text.
    error_handling: If any file is missing or unreadable, abort with an error listing which file failed.

  - name: answer_question
    description: Search indexed documents for the answer to a user question, returning a single-source answer with citation or the refusal template.
    input: User question string and the indexed documents from retrieve_documents.
    output: Answer text with document name and section citation, or the refusal template if no match is found.
    error_handling: If the question could be answered from multiple documents but the answers conflict or blend, refuse and use the template. If no document contains relevant information, use the refusal template exactly.
