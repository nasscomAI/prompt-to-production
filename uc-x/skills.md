skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes their content by document name and section number.
    input: List of file paths — policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: Indexed document store mapping (document_name, section_number) → section text, ready for lookup by answer_question.
    error_handling: If any file is missing or unreadable, halt and surface an error — do not proceed with a partial index, as a missing document would silently cause refusals for valid questions.

  - name: answer_question
    description: Searches the indexed documents for a single-source answer to the user's question and returns it with a citation, or returns the exact refusal template if the question is not covered.
    input: Natural language question string from the user.
    output: |
      Either:
        (a) Answer string containing the factual claim + "Source: <document_name>, section <number>", or
        (b) Exact refusal string: "This question is not covered in the available policy documents
            (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
            Please contact [relevant team] for guidance."
    error_handling: |
      - If the answer requires combining claims from more than one document, return the refusal template — do not blend.
      - If no matching section is found in any document, return the refusal template.
      - Never use hedging phrases ("typically", "generally understood", "while not explicitly covered") under any condition.
