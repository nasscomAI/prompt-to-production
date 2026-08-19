# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy documents, parses them into section-indexed entries keyed by document name and section number, and returns a searchable index ready for single-source lookup.
    input: >
      - doc_paths (list of strings): paths to the three policy files, in this order:
          1. "../data/policy-documents/policy_hr_leave.txt"
          2. "../data/policy-documents/policy_it_acceptable_use.txt"
          3. "../data/policy-documents/policy_finance_reimbursement.txt"
    output: >
      A dict (the index) structured as:
        {
          "policy_hr_leave.txt": {
            "2.3": "Employees must submit a leave application...",
            "5.2": "LWP requires approval from the Department Head and the HR Director...",
            ...
          },
          "policy_it_acceptable_use.txt": { "3.1": "...", ... },
          "policy_finance_reimbursement.txt": { "2.6": "...", ... }
        }
      Each key is the document filename; each sub-key is a section number; each value is
      the verbatim clause body. Prints to stdout: "Indexed [N] sections from [doc]." per document.
    error_handling: >
      If any document file is not found — print the missing path and exit with code 1.
      If a document is empty — print "WARNING: [doc] is empty — skipped." and continue with
      the remaining documents (do not exit; a partial index is still valid).
      If no documents load successfully — exit with code 1.

  - name: answer_question
    description: Searches the document index for the most relevant single-source answer to a question, returns it with a document name and section citation, or returns the exact refusal template if no answer is found.
    input: >
      - question (string): the employee's natural language question.
      - index (dict): the document index returned by retrieve_documents.
    output: >
      A dict with three fields:
        - answer (string): the factual answer drawn from one clause, or the exact refusal
          template if not found.
        - source_doc (string): the document filename the answer came from, or blank on refusal.
        - source_section (string): the section number the answer came from, or blank on refusal.
      Printed to stdout in this format:
        Answer: <answer text>
        Source: <source_doc>, Section <source_section>
        — or on refusal —
        Answer: This question is not covered in the available policy documents
                (policy_hr_leave.txt, policy_it_acceptable_use.txt,
                policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.
        Source: (none)
    error_handling: >
      If the question is blank or whitespace-only — return the refusal template immediately;
      do not attempt a search.
      If the index is empty — return the refusal template; do not invent an answer.
      If keyword matches are found in more than one document — do NOT blend them; use the
      highest-confidence single-document match only, or refuse if confidence is ambiguous.
      Never output an answer that lacks both source_doc and source_section unless it is
      the exact refusal template.
