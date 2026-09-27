skills:

  - name: retrieve_documents
    description: Load and index the three approved policy documents by document name and section number.
    input:
      type: policy document set
      format: Three text files: policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt
    output:
      type: indexed policy collection
      format: Documents retrievable by document name and section number.
    error_handling: Do not add external documents or information. If a document cannot be loaded, report the missing document instead of inventing its contents.

  - name: answer_question
    description: Answer an employee policy question using only one relevant policy document, with an exact source citation, or return the exact refusal template when the question is not covered.
    input:
      type: employee policy question
      format: Natural-language question about company policy.
    output:
      type: policy answer
      format: Direct answer supported by one source document and section number, or the exact refusal template.
    error_handling: Never combine claims from different documents, never use external knowledge or hedging language, never drop conditions or restrictions, and never invent unsupported policy information.

  - name: verify_answer
    description: Check that the proposed answer is grounded in a single approved document and preserves all relevant conditions.
    input:
      type: proposed policy answer
      format: Answer with source document and section citation.
    output:
      type: validation result
      format: PASS when the answer is supported by one document and preserves its conditions; otherwise REFUSE.
    error_handling: Reject answers that contain unsupported claims, cross-document blending, missing citations, dropped conditions, invented section numbers, or hedged statements.