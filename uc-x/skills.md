skills:
  - name: retrieve_documents
    description: Loads all 3 CMC policy .txt files, parses them into an index keyed by document name and section number, and returns the index ready for search.
    input: >
      A list of 3 file paths (strings):
        - path to policy_hr_leave.txt
        - path to policy_it_acceptable_use.txt
        - path to policy_finance_reimbursement.txt
    output: >
      A dict structured as:
        {
          doc_name: {
            "ref": str,          # e.g. "HR-POL-001"
            "sections": {
              "2.3": {
                "section_id": str,
                "text": str      # full clause text
              }, ...
            }
          }, ...
        }
        
      Returns None on any file load failure.
    error_handling: >
      If any of the 3 files cannot be found or read, raise FileNotFoundError
      naming the missing file. If a file is empty or has no recognisable
      clause structure, raise ValueError. Do not return partial indexes —
      all 3 documents must load successfully before the index is returned.

  - name: answer_question
    description: Searches the document index for the best single-source answer to the employee's question, returns a cited answer or the exact refusal template if not covered.
    input: >
      question (str) — the employee's natural-language question.
      doc_index (dict) — the index returned by retrieve_documents.
    output: >
      A dict with keys:
        answer (str)     — the answer text or the exact refusal template.
        source_doc (str) — document filename, or "REFUSAL" if not found.
        section (str)    — section number cited, or "" if refusal.
        is_refusal (bool)— True if the refusal template was used.
      Rules:
        - Answer comes from ONE document only — no cross-document blending.
        - Every answer includes the document reference and section number.
        - If the question is not in any document: is_refusal=True, answer=
          exact refusal template string from agents.md enforcement.
        - If question spans two documents and combining would grant permissions
          not explicitly stated in either: is_refusal=True.
    error_handling: >
      Never raise an exception for "no match found" — return the refusal
      template instead. Raise ValueError only if doc_index is None or empty,
      meaning retrieve_documents failed — the system should not try to answer
      without a valid index.
