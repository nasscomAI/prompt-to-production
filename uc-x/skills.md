# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes their content by document name and section number.
    input: >
      document_paths (list of str): paths to policy_hr_leave.txt,
      policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: >
      An indexed structure mapping each document name and section number to its
      full text content (e.g., {"policy_hr_leave.txt": {"2.6": "...", "5.2": "..."}}).
      All numbered sections are preserved exactly as they appear in the source files.
    error_handling: >
      If any file is missing or unreadable, exit with an error naming the missing
      file. If a file contains no recognizable numbered sections, warn and index
      the raw text under a single entry for manual review.

  - name: answer_question
    description: Searches indexed documents for a single-source answer with citation, or returns the exact refusal template.
    input: >
      question (str): the user's natural language question.
      index (dict): the indexed document structure from retrieve_documents.
    output: >
      Either a single-source answer citing the document name and section number
      (e.g., "Per policy_hr_leave.txt section 2.6, ..."), or the verbatim refusal
      template: "This question is not covered in the available policy documents
      (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
      Please contact [relevant team] for guidance."
    error_handling: >
      If the question matches content in multiple documents, answer from the single
      most directly relevant document only — never blend. If genuine ambiguity exists
      across documents (e.g., the personal phone question touching both IT and HR),
      answer from the document that directly addresses the specific action asked about,
      or use the refusal template. Never hedge with phrases like "while not explicitly
      covered" or "typically".
