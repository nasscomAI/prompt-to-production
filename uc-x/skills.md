# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy .txt files and returns their content as structured sections indexed by document name and section number.
    input: >
      List of file paths to .txt policy documents
      (e.g., ["../data/policy-documents/policy_hr_leave.txt",
              "../data/policy-documents/policy_it_acceptable_use.txt",
              "../data/policy-documents/policy_finance_reimbursement.txt"]).
    output: >
      A list of structured clause entries, each containing:
        - doc_name — the source document filename (e.g., "policy_hr_leave.txt")
        - section_number (e.g., "2.6")
        - section_title (e.g., "ANNUAL LEAVE") — the parent heading
        - clause_text — the full, unmodified text of the clause
    error_handling: >
      If a file does not exist, print: "ERROR: File not found at [path]." and skip it.
      If a file is empty or contains no recognizable numbered clauses, print:
      "WARNING: No structured policy clauses found in [filename]." and skip it.
      If no documents load successfully, exit with: "ERROR: No policy documents could be loaded."

  - name: answer_question
    description: Searches indexed documents for clauses relevant to the user's question and returns a single-source answer with citation or the exact refusal template.
    input: >
      A user question (string) and the full list of indexed clause entries
      as returned by retrieve_documents.
    output: >
      One of two formats:
        (A) Single-source answer: one or more relevant clauses from a SINGLE document,
            each cited as [document_name, Section X.X], preserving all conditions and
            binding verbs from the source.
        (B) Refusal: the exact template —
            "This question is not covered in the available policy documents
            (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
            Please contact [relevant team] for guidance."
    error_handling: >
      If the question is empty or whitespace-only, return: "ERROR: No question provided."
      If relevant clauses are found in multiple documents and blending would be required
      to answer, return the single best-matching document's answer only.
      If no clauses match, return the refusal template.
