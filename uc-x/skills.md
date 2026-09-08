# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 CMC policy files and indexes them by document name and section number for single-source retrieval.
    input: No input required; reads from `../data/policy-documents/` relative to app.py (tries `data/policy-documents/` as fallback). Expects 3 files: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: Dict mapping `document_name -> dict[section_id -> section_text]` plus raw full text per document. Section IDs are of form `X.Y` parsed via regex `^(\d+\.\d+)\s`. Returns also a flat list of all sections with doc provenance for search.
    error_handling: If any file is missing or unreadable, raises FileNotFoundError with explicit path and lists which document failed. If a file has zero parseable sections, logs warning and includes raw text. Never silently substitutes or hallucinates missing content.

  - name: answer_question
    description: Searches indexed documents and returns either a single-source answer with citation OR the verbatim refusal template — never a blend, never hedged.
    input: String `question` (user query). Optional `threshold` float for retrieval confidence (default 0.1).
    output: String answer. On success: factual answer drawn from exactly ONE document, preserving all conditions, plus citation `[Source: <doc>.txt, Section X.Y]`. On failure/unknown: the refusal template verbatim: `This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.` with no prefix/suffix.
    error_handling: >
      If hedging phrases detected ("while not explicitly covered", "typically", "generally", "common practice", "usually") — block and regenerate/refuse.
      If top two documents score within delta or query matches multiple documents with similar confidence — refuse cleanly instead of blending.
      If question matches no section above threshold — return refusal template (not "I don't know" or rephrased). Never combine claims from two documents; never drop qualifiers like "permanent", "maximum 5", "forfeited 31 December", "both required".
