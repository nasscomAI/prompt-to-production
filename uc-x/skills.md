skills:
  - name: "retrieve_documents"
    description: "Loads the 3 approved policy files and indexes their content strictly by document name and section number."
    input:
      file_paths: "list of strings (paths to the HR, IT, and Finance txt files)"
    output:
      document_index: "dictionary mapping document names and section numbers to text content"
    error_handling: "If a document is missing, proceed with the available documents but log a warning."

  - name: "answer_question"
    description: "Searches the indexed documents to return a single-source answer with a strict citation, or outputs the refusal template."
    input:
      question: "string (the user's policy query)"
      document_index: "dictionary (parsed policy sections)"
    output:
      answer: "string (the explicitly cited answer or the exact refusal template)"
    error_handling: "If a question spans multiple documents or causes ambiguity, immediately apply Enforcement Rule 3 (Refusal Template) to prevent cross-document blending."
