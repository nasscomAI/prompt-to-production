# skills.md

skills:
  - name: retrieve_documents
    description: Read policy documents and parse them into section-keyed dictionaries.
    input: Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: Dict of doc -> section -> text.
    error_handling: Missing files trigger FileNotFoundError; malformed sections trigger parse warning.

  - name: answer_question
    description: Answer a question from the indexed policies using single-source logic.
    input: question string and indexed documents.
    output: Text answer plus source citation or refusal template.
    error_handling: If no relevant section, return refusal template exactly.

