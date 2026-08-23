skills:

  - name: retrieve_documents
    description: Loads the three policy documents and indexes their content by document name and section number.
    input: Three policy document file paths in .txt format.
    output: Structured document index containing document names, section numbers, and corresponding policy text.
    error_handling: If a document is missing, unreadable, or has unclear section structure, report the problem and do not invent or infer missing policy content.

  - name: answer_question
    description: Answers a policy question using only one directly supporting document or returns the exact refusal template.
    input: User question as a string and the indexed policy documents from retrieve_documents.
    output: A single-source answer with document filename and section citation for every factual claim, or the exact refusal template.
    error_handling: If the question is unsupported, ambiguous across documents, or would require combining claims from multiple documents, return the exact refusal template rather than guessing or blending information.