skills:
  - name: retrieve_documents
    description: Loads all 3 policy text files from the disk and indexes their content by document name and section number.
    input: file_paths (list of strings) - Paths to the policy files.
    output: list of dicts - The parsed sections, each containing the document reference (e.g., HR-POL-001), document name, section number, section header, and text.
    error_handling: Raise FileNotFoundError if any of the target files do not exist. Return an empty list if no files are loaded.

  - name: answer_question
    description: Searches the indexed sections using keyword overlap to find the single best-matching section for the user's question, formulating a citation-rich response, or returning the refusal template if no matching section is found.
    input:
      question (string) - The user's query.
      indexed_docs (list of dicts) - The indexed policy documents data.
    output: string - The formulated answer citing the document name + section number, or the refusal template.
    error_handling: Return the refusal template if the question is out of scope or doesn't match any section with sufficient confidence.

examples:
  - input:
      question: "Can I carry forward unused annual leave?"
    expected_output: |
      According to policy_hr_leave.txt (HR-POL-001) Section 2.6, employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.
  - input:
      question: "What is the company view on flexible working culture?"
    expected_output: |
      This question is not covered in the available policy documents
      (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
      Please contact the HR Department for guidance.

test_guidance:
  - Run all 7 test questions defined in README.md and assert that no answers blend information from separate files.
  - Assert that out-of-scope questions return the exact refusal template without using hedging language.
