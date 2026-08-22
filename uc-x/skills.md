# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their content by document name and section number.
    input: none required — the three fixed paths under ../data/policy-documents/ (optionally a list of paths to override).
    output: index dict — {document_name (e.g. "policy_hr_leave.txt"): {"title": str, "sections": {section_number: {"heading": str, "clauses": {clause_id: clause_text}}}}} with all wording preserved exactly as written.
    error_handling: Missing or unreadable file → clear error naming the offending file, session exits. A document with no parsable sections → reported at load time. No paraphrasing at index time — retrieval must quote.

  - name: answer_question
    description: Searches the indexed documents for a single-source answer with citation, or returns the refusal template.
    input: question string + document index from retrieve_documents.
    output: dict — {"answer": str (quoted or tightly paraphrased from ONE document), "source": {"document": str, "section": str} or None, "refused": bool}; when refused=True the answer field contains the refusal template verbatim.
    error_handling: Question not covered by any document → refusal template exactly as defined in agents.md, with [relevant team] resolved by topic mapping; never an improvised apology. Relevant clauses found in more than one document with conflicting implications → refuse rather than blend. Partial match where answering would drop conditions → answer only if every condition of that single source is included, otherwise refuse.
