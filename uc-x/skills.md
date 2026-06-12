# skills.md — UC-X "Ask My Documents" Q&A Agent

skills:
  - name: retrieve_documents
    description: Loads all three CMC policy .txt files at startup, parses each into sections and numbered clauses, and builds a searchable index keyed by (document_ref, section_id, clause_id).
    input: >
      doc_paths (list[str]) — list of three absolute or relative paths to the .txt policy files.
      Expected: [policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt].
      Each file uses the same format: divider lines (═══), section headings numbered X. HEADING,
      clauses numbered X.Y with body text on the same and following indented lines.
    output: >
      A list of clause dicts, each with:
        {
          "doc_ref": str,        # e.g. "HR-POL-001"
          "doc_file": str,       # e.g. "policy_hr_leave.txt"
          "doc_title": str,      # e.g. "Employee Leave Policy"
          "section_id": str,     # e.g. "2"
          "section_heading": str,# e.g. "ANNUAL LEAVE"
          "clause_id": str,      # e.g. "2.6"
          "clause_text": str,    # full verbatim clause text
          "tokens": list[str],   # lowercased, stopword-stripped tokens for search
        }
    error_handling: >
      If any file path does not exist: raise FileNotFoundError listing the missing path.
      If a file parses to zero clauses: raise ValueError("No clauses parsed from {path}").
      Partial load (2 of 3 files) is not acceptable — all three must load or the agent exits.

  - name: answer_question
    description: Takes a natural-language question and the loaded clause index, finds the single most relevant clause from a single document, and returns a cited answer or the exact refusal template if no clause is relevant.
    input: >
      question (str) — free-text question from the user.
      index (list[dict]) — the clause list returned by retrieve_documents.
      confidence_threshold (float) — minimum relevance score to produce an answer (default 0.15).
        Below this threshold, the refusal template is returned.
    output: >
      A dict:
        {
          "answer": str,         # the full answer string shown to the user
          "source_doc": str,     # e.g. "HR-POL-001" (empty string if refusal)
          "source_file": str,    # e.g. "policy_hr_leave.txt" (empty if refusal)
          "clause_id": str,      # e.g. "2.6" (empty if refusal)
          "score": float,        # relevance score of top match
          "is_refusal": bool,    # True if refusal template was used
        }
    error_handling: >
      If question is empty or whitespace-only: return the refusal template immediately
        with is_refusal=True — never error on blank input.
      If multiple clauses from DIFFERENT documents have equal top scores:
        choose the clause whose document is most directly related to the question's domain
        (IT keywords → IT-POL-003, leave/absence keywords → HR-POL-001,
        expense/reimbursement keywords → FIN-POL-007) — never merge both into one answer.
      If top-scoring clauses are from the SAME document, combine only adjacent clauses
        from the SAME section into the answer (e.g. 2.5 + 2.6 if both are closely relevant)
        — never pull in clauses from a different section of the same document to pad the answer.
      Never raise an exception during search — always return a result dict.
