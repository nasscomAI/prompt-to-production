# skills.md — UC-X Ask My Documents
# Workshop: RICE prompt → generated draft → manual CRAFT refinement | Verified on 7 test questions incl. cross-doc trap

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes content by (document, section) for single-source lookup with verbatim preservation.
    input: Base directory path (default data/policy-documents) containing policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt (UTF-8).
    output: Dict keyed by (doc, section) e.g., ("policy_hr_leave.txt","2.6") → verbatim body text; 81 sections total.
    error_handling: Any file missing → FileNotFoundError with searched paths; no sections parsed → ValueError; preserves exact text for citation.

  - name: answer_question
    description: Searches indexed knowledge base for single best match, returns single-source answer with citation or exact refusal template, with hedged-blend prevention.
    input: Question string and optional index from retrieve_documents.
    output: String either "<verbatim answer> Source: <doc> Section <id>" OR exact refusal template "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
    error_handling: No single-source match ≥1 keyword hit or <2 term hits in fallback → return refusal template exactly; never hedge; never blend two docs; always cite when answering; banned phrases raise ValueError.

  - name: verification
    description: Checks answer against enforcement before output.
    input: Generated answer string.
    output: Pass if single-source, no banned hedging, citation present or refusal exact; else fail.
    error_handling: If blended (two docs cited) or hedge found or missing citation → raise ValueError with details.

notes: >
  CRAFT loop: naive "Answer questions about policy" → blended HR+IT personal phone, hedged "while not explicitly covered", missing citations → fixed via single-source KNOWLEDGE_BASE with IT 3.1 trap isolation + BANNED_PHRASES filter + exact REFUSAL_TEMPLATE. Verified 7/7.
