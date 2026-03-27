skills:
  - name: retrieve_documents
    description: Loads the three official policy files and indexes their content strictly by document name and specific numbered section.
    input: File paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: A structured index mapping document names and section numbers to the explicit text segments contained within them.
    error_handling: Throws an exception if any of the three configured policy files are missing, unreadable, or missing identifiable sections.

  - name: answer_question
    description: Searches the indexed documents and returns a clean, single-source answer with a strict citation, or explicitly triggers the designated refusal template.
    input: The indexed document structure and the raw user question.
    output: A string containing the direct answer plus citation, or the verbatim refusal string if the answer isn't firmly bound to one single location.
    error_handling: If the question requires spanning multiple documents, causes ambiguity, isn't present, or doesn't map directly to a single isolated rule, it must immediately abort and return the strict refusal template: "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
