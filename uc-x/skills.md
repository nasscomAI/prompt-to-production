# skills.md — UC-X Policy Question Answering Skills

skills:
  - name: retrieve_documents
    description: Loads the three policy text files and parses their content into an indexed structure organized by document name and section/clause numbers.
    input: `directory_path` (str, path to directory containing `policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, and `policy_finance_reimbursement.txt`).
    output: Index dictionary mapping each document file and section number to its parsed text and title.
    error_handling: If any of the policy files are missing or unreadable, raises a FileNotFoundError detailing the missing file.

  - name: answer_question
    description: Queries the indexed policy documents for a given user question and returns a single-source answer with exact citations, or outputs the verbatim refusal template.
    input: `question` (str) and `index` (dictionary produced by `retrieve_documents`).
    output: String response with single-source citation (e.g. `[policy_hr_leave.txt, section 2.6]`) OR the exact refusal template if unmentioned or ambiguous across documents.
    error_handling: If the question cannot be answered from a single authoritative policy section without cross-document blending or hedging, outputs the exact refusal template: "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact the HR/IT/Finance department for guidance."
