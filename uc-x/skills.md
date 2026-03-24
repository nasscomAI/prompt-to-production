# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy files, parses them into structured sections
      indexed by document name and section number for efficient lookup.
    input: >
      A list of file paths (list of str) to the three policy documents:
        - policy_hr_leave.txt
        - policy_it_acceptable_use.txt
        - policy_finance_reimbursement.txt
    output: >
      A searchable index structured as:
        - document_name (str): The filename of the policy document.
        - sections (list): Each containing:
            - section_number (str): e.g., "2.3", "5.2".
            - heading (str): Section heading if present.
            - body (str): Full clause text, preserved verbatim.
      Total section count per document is reported for verification.
    error_handling: >
      If any file does not exist or cannot be read: report which file
      failed and continue loading the remaining files. Flag missing
      documents clearly so the answer skill knows which sources are
      unavailable.

  - name: answer_question
    description: >
      Searches the indexed documents for clauses relevant to the user's
      question and returns a single-source answer with citation, or the
      exact refusal template if the question is not covered.
    input: >
      Two parameters:
        - question (str): The user's natural language question.
        - document_index: The structured index from retrieve_documents.
    output: >
      One of two responses:
        - Factual answer: A clear statement citing source document name and
          section number (e.g., "Per policy_hr_leave.txt section 2.6:"),
          preserving all conditions, limits, and binding verbs exactly.
        - Refusal: The exact template — "This question is not covered in
          the available policy documents (policy_hr_leave.txt,
          policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
          Please contact [relevant team] for guidance."
    error_handling: >
      If the question matches clauses in multiple documents: answer from
      the single most directly relevant document only. Do NOT blend.
      If genuine ambiguity exists across documents: use the refusal
      template and explain that the question spans multiple policy domains.
      Never guess, hedge, or synthesize across sources.
