skills:
  - name: retrieve_documents
    description: loads all 3 policy files, indexes by document name and section number
    input: list of document file paths (e.g., policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt)
    output: indexed documents containing section numbers and text content
    error_handling: Return an error if any of the required documents cannot be found or loaded.

  - name: answer_question
    description: searches indexed documents, returns single-source answer + citation OR refusal template
    input: user search query/question and the structured indexed documents
    output: string containing a single-source answer with document and section citation, or the refusal template
    error_handling: If the answer is ambiguous, requires blending documents, or isn't found, return the exact refusal template.
