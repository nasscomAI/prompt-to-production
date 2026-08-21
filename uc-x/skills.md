# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy .txt files and returns their content indexed by document name and section number, ready for single-source lookup.
    input: >
      A list of three file paths (strings):
        - ../data/policy-documents/policy_hr_leave.txt
        - ../data/policy-documents/policy_it_acceptable_use.txt
        - ../data/policy-documents/policy_finance_reimbursement.txt
      All three must be loaded on startup — partial loading is not permitted.
    output: >
      A nested dict (the index) structured as:
        {
          "policy_hr_leave": {
            "2.3": "14-day advance notice required...",
            "2.4": "Written approval required...",
            ...
          },
          "policy_it_acceptable_use": { "3.1": "...", ... },
          "policy_finance_reimbursement": { "3.1": "...", ... }
        }
      Keys are document names (filename without extension) and section numbers exactly
      as they appear in the source. Content is the verbatim section text.
    error_handling: >
      If any of the three files does not exist: raise FileNotFoundError naming the
      missing file — do not proceed with a partial index.
      If a file contains no numbered sections: load the full text under key "FULL_TEXT"
      and log a warning — do not silently return an empty index for that document.

  - name: answer_question
    description: Takes a user question and the document index, searches for a single-source answer with a section citation, and returns either a cited factual answer or the exact refusal template — never a blend from two documents.
    input: >
      Two arguments:
        - question (string) — the user's natural-language policy question
        - index (dict) — the nested index returned by retrieve_documents
    output: >
      One of exactly two response formats:
        1. Cited answer (when the question is covered by a single document):
           "[Answer text]. Source: {document_name}, section {section_number}."
           The answer must be drawn from one document only — no combining.
        2. Exact refusal template (when the question is not in any document, or
           when combining two documents would be required):
           "This question is not covered in the available policy documents
           (policy_hr_leave.txt, policy_it_acceptable_use.txt,
           policy_finance_reimbursement.txt).
           Please contact [relevant team] for guidance."
      Critical: the personal-phone question ("Can I use my personal phone to access
      work files when working from home?") must be answered from policy_it_acceptable_use
      section 3.1 only — do NOT blend with HR remote-work references.
    error_handling: >
      If the question string is empty: return the refusal template — do not attempt
      to search or guess.
      If the index is empty or missing: raise ValueError("Document index is not loaded.
      Call retrieve_documents first.").
      If hedging phrases are detected in a candidate answer ("while not explicitly
      covered", "typically", "generally understood", "it is common practice",
      "employees are generally expected to"): discard that candidate and return the
      refusal template instead — never let hedged output reach the user.
