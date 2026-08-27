skills:
  - name: retrieve_documents
    description: Loads all available policy text files and indexes their numbered sections by document name and section number.
    input:
      type: object
      format: "{ document_paths: Array<string> }"
    output:
      type: object
      format: "{ documents: Array<{ name: string, sections: Array<{ section: string, text: string }> }> }"
    error_handling: >
      If any input file is missing or unreadable, raise an error; if numbered sections cannot be extracted from a document, return that document with an empty sections list and include a clear warning.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with a citation or the exact refusal template when the question is not covered.
    input:
      type: object
      format: "{ question: string, documents: Array<{ name: string, sections: Array<{ section: string, text: string }> }> }"
    output:
      type: object
      format: "{ answer: string, citation: string, refusal: boolean }"
    error_handling: >
      If the question is not covered by any document, return the exact refusal template with refusal=true; if multiple documents are equally relevant, return the refusal template rather than blending sources.
