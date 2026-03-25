skills:
  - name: retrieve_documents
    description: Loads all 3 policy documents (HR, IT, Finance) and parses them for indexing.
    input: None — assumes documents exist at specified paths.
    output: A collection of strings or objects representing document sections, indexed by document name and section number.
    error_handling: If a document is missing, the system warns the user and proceeds with the remaining documents.

  - name: answer_question
    description: Searches indexed documents to provide a single-source answer with a citation or the refusal template if not found.
    input: Question (string) + Indexed documents (as provided by retrieve_documents).
    output: Answer (string) containing factual claim + citation (Doc Name + Section #), OR the mandatory refusal template.
    error_handling: If a question is ambiguous or leads to cross-document blending, it must either pick a single source or use the refusal template.
