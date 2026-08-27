skills:
  - name: retrieve_documents
    description: >
      Loads all three policy files from ../data/policy-documents/,
      parses each into a structured index of document name, section
      headings (e.g., "2. ANNUAL LEAVE"), and section numbers
      (e.g., "section 2.6"). Returns the index for downstream
      searching.
    input: >
      None (files are read from the known path
      ../data/policy-documents/).
    output: >
      A dictionary keyed by document filename, each value being a
      list of {section_number, heading, text} entries.
    error_handling: >
      If a file is missing or unreadable, raise FileNotFoundError
      with the filename. Do not proceed with partial data.

  - name: answer_question
    description: >
      Accepts a natural-language question string, searches the
      indexed documents (from retrieve_documents), and returns
      either a single-source answer with a document + section
      citation, or the exact refusal template.
    input: >
      A plain-text question string.
    output: >
      A plain-text answer string: either (a) the answer with
      citation like "policy_hr_leave.txt section 2.6", or (b)
      the verbatim refusal template:
      "This question is not covered in the available policy documents
      (policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt). Please contact [relevant team]
      for guidance."
    error_handling: >
      If the question is ambiguous or no single document covers it,
      return the refusal template verbatim. Never blend answers
      from multiple documents.
