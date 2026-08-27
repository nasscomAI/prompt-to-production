skills:
  - name: retrieve_documents
    description: loads all 3 policy files, indexes by document name and section number
    input: File paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt
    output: Indexed policy content organized exactly by document name and section number
    error_handling: Re-attempt load or abort if any document fails to be properly indexed and loaded.

  - name: answer_question
    description: searches indexed documents, returns single-source answer + citation OR refusal template
    input: The user's question and the output from retrieve_documents
    output: A factual single-source answer with document name and section citation, or the exact refusal template
    error_handling: Must output the absolute refusal template if the answer is missing, requires combining multiple documents, or is in any way ambiguous.
