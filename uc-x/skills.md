# skills.md — UC-X Ask My Documents

Aligned with `uc-x/README.md` and the enforcement rules that belong in `agents.md`.

---

skills:
  - name: retrieve_documents
    description: Loads the three policy corpora and builds a retrievable index keyed by document basename and section number so answers can cite a single source.
    input: "Optional base path; defaults to ../data/policy-documents/ containing policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt (UTF-8 text)."
    output: "An in-memory structure (or equivalent) mapping document name → ordered sections (section id/heading + body text) suitable for lookup without merging documents."
    error_handling: "If a file is missing or unreadable, surface a clear error and do not synthesize policy text. Do not preload answers—only raw document content."

  - name: answer_question
    description: Takes a natural-language question, retrieves only what is needed from one document at a time, and returns either a single-source factual answer with citation or the verbatim refusal template—never a cross-document blend.
    input: "String question from the user; read access to the index produced by retrieve_documents."
    output: "Either (1) answer text plus citation in the form document name + section number for every factual claim, or (2) the exact refusal template from agents.md/README when the question is not covered or would require blending sources."
    error_handling: "If the question matches no section, output the refusal template word-for-word (no paraphrase). If multiple docs seem relevant, pick the single document that actually contains the fact; if none contains a straight answer or combining HR+IT would be required for the trap question, refuse per template rather than merge. Reject hedged answers: no 'while not explicitly covered', 'typically', 'generally understood', or similar."
