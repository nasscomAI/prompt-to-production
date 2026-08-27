skills:
  - name: retrieve_documents
    description: Loads and processes the three policy text files, indexing them by document name and section/clause number.
    input:
      type: string
      format: "The folder path containing the policy documents (e.g. data/policy-documents)."
    output:
      type: dict
      format: "A nested dictionary mapping document filenames to their parsed clauses and sections."
    error_handling: >
      If any of the three files are missing, logs an error and raises a FileNotFoundError.

  - name: answer_question
    description: Evaluates an employee question against the indexed policies, returning a single-source answer with citation or the exact refusal template.
    input:
      type: parameters
      format: "query: string, indexed_docs: dict"
    output:
      type: string
      format: "A text response containing the cited answer or the exact refusal template."
    error_handling: >
      If the question is out of scope or requires combining different sources, returns the exact refusal template: 'This question is not covered in the available policy documents...'.
