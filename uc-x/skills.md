# skills.md

skills:
  - name: retrieve_documents
    description: loads all 3 policy files, indexes by document name and section number
    input: 3 documents that describe policy followed in a company in .txt format
    output: returns the content of the documents referencing the section it pulled out from and the phrase it pulled out from the section
    error_handling: "Refusal condition: This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."

  - name: answer_question
    description: searches indexed documents, returns single-source answer + citation OR refusal template
    input: user provides a string as a question in cli
    output: returns the answer to the question in a string format
    error_handling: "Refusal condition: This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."

input files:

../data/policy-documents/policy_hr_leave.txt
../data/policy-documents/policy_it_acceptable_use.txt
../data/policy-documents/policy_finance_reimbursement.txt

example of the final command: python app.py

the user then inputs their question in the CLI and the model returns the answer to the question in a string format. Example Question - "Can I carry forward unused annual leave?".
Example response - "HR policy section 2.6 — exact limit, exact forfeiture date"