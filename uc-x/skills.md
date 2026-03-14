skills:
  - name: retrieve_documents
    description: Fetches documents and converts into an Index
    input: Text Files policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt
    output: Index of documents 
    error_handling: Reports error if documents are not found

  - name: answer_question
    description: Answers questions based on the index of documents
    input: question
    output: Answer to the question
    error_handling: Respond with the message "This question is not covered in the available policy documents 
    (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
