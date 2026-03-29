# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

## Refusal Template
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [AskHR@abcd.com] for guidance.

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: File paths to the policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: A dictionary indexed by document name and section number containing the content.
    error_handling: Raises an error if any file is not found or cannot be read.

  - name: answer_question
    description: Searches the indexed documents for an answer to a question, returning a single-source answer with citation or the refusal template if not covered. Matches answers by finding exact or closely related content from a single document only, never combining claims from multiple documents.
    input: A question string.
    output: A string containing the answer with source citation (document name + section number), or the refusal template if the question is not covered in the documents.
    error_handling: Uses the refusal template exactly for questions not in the documents, if combining documents would be required, or if the answer would require hedging phrases. Never uses phrases like "while not explicitly covered", "typically", or "generally understood".
