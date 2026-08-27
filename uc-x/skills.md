# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files (HR, IT, Finance) and indexes their contents by document name and section number.
    input: Filepaths to the 3 policy documents (list of strings).
    output: A structured index object mapping (document_name, section_number) to raw text content.
    error_handling: Halts execution if any document is unreadable or missing.

  - name: answer_question
    description: Searches the indexed documents for an exact answer to the user's question and returns the answer with a citation, or the exact refusal template.
    input: The structured index object from retrieve_documents, and the user's question (string).
    output: A formatted string containing the single-source answer and citation, OR the exact verbatim refusal template.
    error_handling: Triggers the exact refusal template if no single section contains the complete answer, or if multiple sections conflict/blend.
