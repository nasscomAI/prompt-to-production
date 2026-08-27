# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 CMC policy files and indexes their content by document name and section number.
    input: No input required — file paths are fixed:
      policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: A dict mapping (document_name, section_number) → section text, e.g.
      ('policy_it_acceptable_use.txt', '3.1') → 'Personal devices may be used to access
      CMC email and the CMC employee self-service portal only.'
    error_handling: If any of the 3 files is missing or unreadable, raise an error
      identifying the missing file and halt — do not answer questions with partial data.

  - name: answer_question
    description: Returns a single-source answer with citation using a two-stage approach — deterministic pattern rules first, keyword fallback second — or the exact refusal template if no safe single-source answer exists.
    input: A natural language question (string) and the indexed document structure
      produced by retrieve_documents.
    output: A plain-text answer in the format:
      '[Answer text]. (Source: [document_name], section [X.Y])'
      OR the exact refusal template if the question is not covered or requires blending.
    error_handling: |
      Stage 1 — Pattern rules (deterministic, checked first):
        Each rule is a regex pattern matched against the lowercased question.
        Cross-document trap patterns (e.g. personal phone + work files) → always refuse.
        Known single-source patterns (e.g. 'carry forward', 'install Slack', 'who approves LWP')
        → return the mapped section directly.
      Stage 2 — Keyword fallback (for questions not matched by patterns):
        Expand abbreviations and brand names (DA→daily allowance, Slack→software,
        laptop→device, phone→personal device, approves→approval).
        Score each section by keyword overlap using prefix matching for words ≥5 chars.
        Cross-document ratio guard: if second-best document scores ≥60% of top document
        score, the question is ambiguous → return refusal template.
        If no section scores > 0, return refusal template.
