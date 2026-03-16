# skills.md

skills:
  - name: retrieve_documents
    description: >
      Load the three policy documents and build an index keyed by document name and section number.
    input:
      type: object
      format: |
        {
          "paths": [
            "../data/policy-documents/policy_hr_leave.txt",
            "../data/policy-documents/policy_it_acceptable_use.txt",
            "../data/policy-documents/policy_finance_reimbursement.txt"
          ]
        }
    output:
      type: object
      format: |
        {
          "documents": [
            {
              "document_name": "policy_it_acceptable_use.txt",
              "sections": [
                { "section": "3.1", "text": "..." }
              ]
            }
          ]
        }
    error_handling: >
      If any path cannot be loaded or section numbers cannot be reliably identified, fail closed and
      return an error stating which document/path failed; do not invent sections or content.

  - name: answer_question
    description: >
      Answer a user question using the indexed documents, returning a single-source answer with citations
      for every factual claim OR the refusal template verbatim if the answer is not present in the documents.
    input:
      type: object
      format: |
        {
          "question": "string",
          "documents": { "documents": [ /* output of retrieve_documents */ ] }
        }
    output:
      type: object
      format: |
        {
          "type": "answer" | "refusal",
          "answer": "string",
          "citations": [
            { "document_name": "policy_it_acceptable_use.txt", "section": "3.1" }
          ]
        }
    error_handling: |
      - If the question is not covered in the available policy documents, return type="refusal" and use
        this exact refusal text (no variations):
        This question is not covered in the available policy documents
        (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
        Please contact [relevant team] for guidance.
      - Never blend multiple documents into one answer. If relevant content appears in more than one document
        and a single-document answer would be incomplete or ambiguous, return the refusal template.
