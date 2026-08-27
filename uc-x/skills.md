skills:
  - name: retrieve_documents
    description: >
      Loads all three policy files (policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt) and indexes their content by document name
      and section number for lookup.
    input: >
      No input. Operates on the fixed set of files at
      ../data/policy-documents/policy_*.txt.
    output: >
      An indexed dictionary mapping document names and section numbers to their
      text content, ready for search.
    error_handling: >
      If a file is missing or unreadable, return an error listing exactly which
      file could not be loaded. Do not proceed with partial data.

  - name: answer_question
    description: >
      Searches the indexed documents for a user question and returns a
      single-source answer with citation, or the refusal template if the
      question is not covered.
    input: >
      A free-text question string from the user.
    output: >
      One of two outputs:
      1. An answer citing exactly one document name and section number for
         every factual claim, with no claims from any other document.
      2. The verbatim refusal template:
         "This question is not covered in the available policy documents
         (policy_hr_leave.txt, policy_it_acceptable_use.txt,
         policy_finance_reimbursement.txt). Please contact [relevant team]
         for guidance."
    error_handling: >
      Never combine claims from two different documents into a single answer.
      Never use hedging phrases: 'while not explicitly covered', 'typically',
      'generally understood', 'it is common practice', or any equivalent.
      If no matching section is found in any document, or if the question
      spans multiple documents, respond with the verbatim refusal template.
