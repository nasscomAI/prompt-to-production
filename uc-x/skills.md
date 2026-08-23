skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: List of paths to the policy documents (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: Indexed text structured by document name and section number.
    error_handling: Return an error if a document cannot be found or read.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with citation, or the exact refusal template.
    input: A user query and the indexed policy documents text.
    output: A clear, single-source factual answer paired with its document name and section citation, OR the exact refusal template.
    error_handling: If the answer requires blending documents or the information is not clearly found, output the exact refusal template: "This question is not covered in the available policy documents\n(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\nPlease contact [relevant team] for guidance."
