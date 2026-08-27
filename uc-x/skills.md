skills:
  - name: retrieve_documents
    description: Loads all 3 required policy files and extracts content strictly structured by document name and section number (e.g., 2.3, 3.1) while preserving exact text without modification.
    input: file paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt
    output: structured mapping → {document_name: {section_number: exact_text}}
    error_handling: |
      - If any required file is missing or unreadable → FAIL immediately
      - If section extraction fails or sections are not properly detected → FAIL
      - If document structure is inconsistent or incomplete → FAIL
      - No partial loading allowed under any condition

  - name: answer_question
    description: Answers a user query strictly using a single document source, returning exact text with mandatory citation (document name and section number). No cross-document reasoning allowed.
    input: user question (string) and structured policy data
    output: |
      Answer: <exact extracted answer>
      Source: <document_name> — Section <section_number>
    error_handling: |
      - If answer is not found in any single document → return refusal template
      - If answering requires combining multiple documents → return refusal template
      - If section match is ambiguous → return refusal template
      - If citation (document + section) cannot be provided → FAIL
      - Partial answers are NOT allowed
      - No hallucination, no assumptions, no generalization

      EXACT refusal template:
      This question is not covered in the available policy documents
      (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
      Please contact the relevant department for guidance.