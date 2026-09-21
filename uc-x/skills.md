skills:
  - name: retrieve_documents
    description: Loads the three policy files and indexes their numbered sections by document name.
    input: "Directory containing policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt."
    output: "Dictionary indexed by filename and section number, with source text for each section."
    error_handling: "Rejects missing or unreadable policy files and never substitutes external or inferred content."

  - name: answer_question
    description: Finds a single-source policy answer with citation or returns the exact refusal template.
    input: "A staff question string and the indexed policy sections."
    output: "A cited answer supported by one document, or the required refusal sentence."
    error_handling: "Refuses unsupported or cross-document questions, avoids hedging, and does not blend claims from separate policies."
