# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, parses them into structured sections indexed by document name and section number for fast lookup.
    input: >
      A list of file paths (strings) pointing to the three policy .txt files.
    output: >
      A dictionary indexed by document filename, where each entry contains a
      list of sections with: section_number (string), section_title (string),
      section_body (string). Also reports total sections loaded per document.
    error_handling: >
      If any file is missing or unreadable, print a warning for that file and
      continue loading the others. If no files can be loaded, print error and exit.

  - name: answer_question
    description: Searches the indexed documents for the answer to a user question, returning a single-source cited answer or the exact refusal template.
    input: >
      A question string from the user, plus the indexed document dictionary
      from retrieve_documents.
    output: >
      One of:
      (a) A factual answer string with citation in format
          "Answer: [text]. Source: [filename], Section [number]"
      (b) The exact refusal template:
          "This question is not covered in the available policy documents
          (policy_hr_leave.txt, policy_it_acceptable_use.txt,
          policy_finance_reimbursement.txt). Please contact [relevant team]
          for guidance."
    error_handling: >
      If the question matches content in multiple documents and cannot be
      answered from a single source without blending, respond with the answer
      from the most directly relevant document only. If genuine ambiguity
      exists between two sources, use the refusal template rather than blend.
      Never guess or hedge.
