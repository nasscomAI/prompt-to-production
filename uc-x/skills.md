# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy text files and indexes their content by document name and section number for efficient searching.
    input: List of file paths to the three policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: Returns a dictionary indexed by document name, where each document contains structured sections with section numbers and content. Example: {"policy_hr_leave.txt": {"2.6": "Employees may carry forward..."}}
    error_handling: If any policy file is missing, raises FileNotFoundError listing which files are missing. If files cannot be parsed for section numbers, raises ValueError with parsing error details.

  - name: answer_question
    description: Searches indexed policy documents for answer to user question, returning either a single-source answer with citation or the refusal template.
    input: User question string and indexed documents dictionary from retrieve_documents.
    output: Returns answer string that is either: (1) factual answer from ONE document with citation format "[Source: policy_name.txt section X.Y]", OR (2) refusal template verbatim: "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact the HR Department for guidance."
    error_handling: If question matches content in multiple documents, returns answer from the most specific/relevant source with citation. Never blends multiple sources. Never uses hedging language. If genuinely ambiguous or not covered, returns refusal template exactly as specified.
